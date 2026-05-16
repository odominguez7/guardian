# Copyright 2026 GUARDIAN
# Species ID tools — Gemini Vision + Vertex AI Search corpus lookup.
#
# Two tools:
#   identify_species(image_uri)        — Gemini Vision returns species, behavior, count.
#   lookup_species_factsheet(name)     — Queries the guardian-collection
#                                        Vertex AI Search data store for the
#                                        species fact sheet (IUCN status,
#                                        CITES appendix, threat signals,
#                                        TNFD reporting framework).

import json
import logging
import os
from typing import Optional

import google.auth
from google import genai
from google.api_core.exceptions import GoogleAPIError
from google.cloud import discoveryengine_v1
from google.genai import types as genai_types

logger = logging.getLogger(__name__)

_DEFAULT_VISION_MODEL = os.environ.get("SPECIES_ID_MODEL", "gemini-2.5-pro")
_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
_SEARCH_DATA_STORE = os.environ.get("GUARDIAN_SEARCH_DATA_STORE", "guardian-collection")
_SEARCH_LOCATION = os.environ.get("GUARDIAN_SEARCH_LOCATION", "global")

_client: "genai.Client | None" = None
_search_client: "discoveryengine_v1.SearchServiceClient | None" = None


def _get_client() -> "genai.Client":
    global _client
    if _client is None:
        _, project_id = google.auth.default()
        _client = genai.Client(vertexai=True, project=project_id, location=_LOCATION)
    return _client


def _get_search_client() -> "discoveryengine_v1.SearchServiceClient":
    global _search_client
    if _search_client is None:
        _search_client = discoveryengine_v1.SearchServiceClient()
    return _search_client


_SPECIES_ID_PROMPT = """You are GUARDIAN's Species ID Agent.

Look at the provided image and identify the wildlife species present. Return a SINGLE JSON object — no prose, no markdown — with this schema:

{
  "primary_species": {
    "common_name": str,
    "scientific_name": str,
    "count": int,
    "confidence": float
  },
  "secondary_species": [{"common_name": str, "scientific_name": str, "count": int, "confidence": float}],
  "individual_animal_hints": [str],     // notable markings, age class, body condition (e.g. "broken left tusk", "matriarch posture", "calf at heel")
  "behavior_observed": [str],            // e.g. ["grazing", "alert posture", "fleeing", "matriarchal herd cohesion"]
  "habitat_inference": str,              // brief: ecosystem the image suggests
  "endangered_listed": bool,             // True if any identified species is IUCN Endangered/Critically Endangered
  "overall_confidence": float,
  "explanation": str                     // 1-sentence rationale a ranger would understand
}

Be conservative: if uncertain, lower confidence. Never invent species.
"""


def identify_species(image_uri: str, focus: Optional[str] = None) -> dict:
    """Identify wildlife species + behavior from an image.

    Use this tool when given a still image from a camera trap, ranger photo,
    or any wildlife scene. Returns species ID + behavior + individual-animal
    hints (markings, age, condition) the orchestrator can route to specialist
    agents (Pattern for historical cross-ref, Sponsor for compliance flag).

    Args:
        image_uri: gs://, https://, or data URI to a JPEG/PNG/WEBP image.
        focus: Optional focus instruction (e.g. "identify the individual
            elephant by ear notches" or "estimate herd size").

    Returns:
        Dict with status, primary_species, secondary_species,
        individual_animal_hints, behavior_observed, habitat_inference,
        endangered_listed, overall_confidence, explanation,
        _source_uri, _model. status="error" with error field on failure.
    """
    if not image_uri:
        return {"status": "error", "error": "image_uri is required"}

    instruction = _SPECIES_ID_PROMPT
    if focus:
        instruction += f"\n\nADDITIONAL FOCUS: {focus}"

    try:
        part = _build_image_part(image_uri)
        response = _get_client().models.generate_content(
            model=_DEFAULT_VISION_MODEL,
            contents=[part, instruction],
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )
        parsed = json.loads(response.text)
        parsed["status"] = "ok"
        parsed["_source_uri"] = image_uri
        parsed["_model"] = _DEFAULT_VISION_MODEL
        return parsed
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "error": f"Model returned non-JSON output: {e}",
            "_raw_text": getattr(response, "text", "")[:500] if "response" in locals() else "",
        }
    except Exception as e:
        logger.warning("identify_species failed for %s: %s", image_uri, e)
        return {"status": "error", "error": f"{type(e).__name__}: {e}"}


def lookup_species_factsheet(common_name: str) -> dict:
    """Fetch the species fact sheet from the guardian-collection Vertex AI Search corpus.

    Returns IUCN status, CITES appendix, key threats, threat-signal indicators,
    and the TNFD / CSRD reporting framework references the orchestrator uses
    to decide whether the incident requires sponsor + funder fan-out. This is
    the agentic RAG step: Species ID → corpus → routing decision.

    Args:
        common_name: Common name (e.g. "African elephant", "Black rhinoceros").
            Scientific name also accepted.

    Returns:
        Dict with status, common_name, top_match (the highest-scoring corpus
        doc with iucn_status, cites_appendix, habitat, range, raw_text excerpt),
        and other_matches (list of weaker matches with common_name + score).
    """
    if not common_name:
        return {"status": "error", "error": "common_name is required"}

    try:
        _, project_id = google.auth.default()
    except Exception as e:
        return {"status": "error", "error": f"adc_unavailable: {e}"}

    serving_config = (
        f"projects/{project_id}/locations/{_SEARCH_LOCATION}/collections/"
        f"default_collection/dataStores/{_SEARCH_DATA_STORE}/servingConfigs/default_search"
    )

    request = discoveryengine_v1.SearchRequest(
        serving_config=serving_config,
        query=common_name,
        page_size=5,
        content_search_spec=discoveryengine_v1.SearchRequest.ContentSearchSpec(
            snippet_spec=discoveryengine_v1.SearchRequest.ContentSearchSpec.SnippetSpec(
                return_snippet=True,
            ),
        ),
    )

    try:
        response = _get_search_client().search(request=request)
    except GoogleAPIError as e:
        return {"status": "error", "error": f"search_failed: {type(e).__name__}: {e}"}

    results = []
    for result in response.results:
        doc = result.document
        struct = dict(doc.struct_data) if doc.struct_data else {}
        derived = dict(doc.derived_struct_data) if doc.derived_struct_data else {}
        snippets = derived.get("snippets", []) or []
        snippet_text = ""
        if snippets and isinstance(snippets[0], dict):
            snippet_text = snippets[0].get("snippet", "")
        results.append(
            {
                "doc_id": doc.id,
                "common_name": struct.get("common_name"),
                "scientific_name": struct.get("scientific_name"),
                "iucn_status": struct.get("iucn_status"),
                "cites_appendix": struct.get("cites_appendix"),
                "habitat": struct.get("habitat", []),
                "range": struct.get("range", []),
                "snippet": snippet_text,
            }
        )

    if not results:
        return {
            "status": "ok",
            "common_name": common_name,
            "top_match": None,
            "other_matches": [],
            "note": "No corpus match. Treat as unlisted; do not file TNFD without manual review.",
        }

    return {
        "status": "ok",
        "common_name": common_name,
        "top_match": results[0],
        "other_matches": results[1:],
        "_data_store": _SEARCH_DATA_STORE,
    }


def _build_image_part(uri: str) -> genai_types.Part:
    mime = _infer_image_mime(uri)
    return genai_types.Part.from_uri(file_uri=uri, mime_type=mime)


def _infer_image_mime(uri: str) -> str:
    lower = uri.lower()
    if lower.endswith(".png"):
        return "image/png"
    if lower.endswith(".webp"):
        return "image/webp"
    return "image/jpeg"
