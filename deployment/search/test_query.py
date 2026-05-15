"""GUARDIAN — quick smoke test that the corpus is queryable.

Usage:
    .venv/bin/python deployment/search/test_query.py "rhino poaching threat indicators"
"""

from __future__ import annotations

import sys

import google.auth
from google.cloud import discoveryengine_v1

LOCATION = "global"
COLLECTION = "default_collection"
DATA_STORE_ID = "guardian-collection"
SEARCH_ENGINE_ID = "guardian-search-dev"
SERVING_CONFIG = "default_search"


def main(query: str) -> int:
    _, project_id = google.auth.default()
    serving_path = (
        f"projects/{project_id}/locations/{LOCATION}/collections/{COLLECTION}/"
        f"engines/{SEARCH_ENGINE_ID}/servingConfigs/{SERVING_CONFIG}"
    )

    client_options = None
    client = discoveryengine_v1.SearchServiceClient(client_options=client_options)
    request = discoveryengine_v1.SearchRequest(
        serving_config=serving_path,
        query=query,
        page_size=5,
        query_expansion_spec=discoveryengine_v1.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine_v1.SearchRequest.QueryExpansionSpec.Condition.AUTO,
        ),
        spell_correction_spec=discoveryengine_v1.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine_v1.SearchRequest.SpellCorrectionSpec.Mode.AUTO,
        ),
    )

    print(f"Query: '{query}'")
    print(f"Serving: {serving_path}")
    print()

    response = client.search(request=request)
    for i, result in enumerate(response.results, 1):
        doc = result.document
        struct = dict(doc.struct_data) if doc.struct_data else {}
        print(f"--- Result #{i} ---")
        print(f"  id:           {doc.id}")
        print(f"  doc_type:     {struct.get('doc_type', '?')}")
        if struct.get("scientific_name"):
            print(f"  species:      {struct['scientific_name']} ({struct.get('common_name', '')})")
            print(f"  iucn:         {struct.get('iucn_status', '?')}")
            print(f"  cites:        {struct.get('cites_appendix', '?')}")
        elif struct.get("framework_name"):
            print(f"  framework:    {struct['framework_name']}")
        elif struct.get("title"):
            print(f"  title:        {struct['title']}")
        print()

    return 0


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "rhino poaching threat detection"
    sys.exit(main(q))
