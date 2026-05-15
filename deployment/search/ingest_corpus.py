"""GUARDIAN — ingest the wildlife corpus into the Vertex AI Search data store.

Reads JSON docs from sample_data/wildlife_corpus/, uploads them to GCS,
and triggers a bulk import into the data store.

Usage:
    .venv/bin/python deployment/search/ingest_corpus.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import google.auth
from google.api_core.exceptions import AlreadyExists
from google.cloud import discoveryengine_v1, storage

# --- Config -------------------------------------------------------------------
LOCATION = "global"
COLLECTION = "default_collection"
DATA_STORE_ID = "guardian-collection"
BRANCH = "default_branch"  # standard Discovery Engine branch

CORPUS_DIR = Path(__file__).resolve().parents[2] / "sample_data" / "wildlife_corpus"


def main() -> int:
    _, project_id = google.auth.default()
    print(f"Project: {project_id}")

    docs = sorted(CORPUS_DIR.glob("*.json"))
    if not docs:
        print(f"No JSON docs found in {CORPUS_DIR}", file=sys.stderr)
        return 1
    print(f"Found {len(docs)} corpus document(s):")
    for d in docs:
        print(f"  - {d.name}")

    bucket_name = f"{project_id}-guardian-docs"

    # 1. Ensure GCS bucket exists
    storage_client = storage.Client(project=project_id)
    try:
        bucket = storage_client.create_bucket(bucket_name, location="us-central1")
        print(f"✓ Created GCS bucket: gs://{bucket_name}")
    except AlreadyExists:
        bucket = storage_client.bucket(bucket_name)
        print(f"✓ GCS bucket exists: gs://{bucket_name}")

    # 2. Upload corpus docs + build the import JSONL
    #    Discovery Engine ingestion via JSONL: one Document JSON per line at a GCS URI.
    jsonl_lines = []
    for path in docs:
        with open(path, encoding="utf-8") as f:
            doc_dict = json.load(f)
        # Strip rawText into a separate uploaded file, leave structData inline.
        # Simpler approach: include rawText inline via Document.content.raw_bytes
        # would require base64; use the gcs-uri-content path instead.
        raw_text = doc_dict["content"]["rawText"]
        text_blob_name = f"corpus/{path.stem}.txt"
        bucket.blob(text_blob_name).upload_from_string(
            raw_text, content_type="text/plain"
        )
        text_gcs_uri = f"gs://{bucket_name}/{text_blob_name}"

        import_doc = {
            "id": doc_dict["id"],
            "schemaId": "default_schema",
            "structData": doc_dict["structData"],
            "content": {
                "mimeType": "text/plain",
                "uri": text_gcs_uri,
            },
        }
        jsonl_lines.append(json.dumps(import_doc))
        print(f"  uploaded {path.stem}.txt → {text_gcs_uri}")

    # Write the JSONL manifest to GCS for the import operation
    manifest_blob = "corpus/_manifest.jsonl"
    bucket.blob(manifest_blob).upload_from_string(
        "\n".join(jsonl_lines) + "\n", content_type="application/jsonl"
    )
    manifest_uri = f"gs://{bucket_name}/{manifest_blob}"
    print(f"✓ Wrote import manifest: {manifest_uri}")

    # 3. Trigger import
    doc_client = discoveryengine_v1.DocumentServiceClient()
    parent_branch = (
        f"projects/{project_id}/locations/{LOCATION}/collections/{COLLECTION}/"
        f"dataStores/{DATA_STORE_ID}/branches/{BRANCH}"
    )

    print(f"Triggering import into {parent_branch}...")
    op = doc_client.import_documents(
        request=discoveryengine_v1.ImportDocumentsRequest(
            parent=parent_branch,
            gcs_source=discoveryengine_v1.GcsSource(
                input_uris=[manifest_uri],
                data_schema="document",
            ),
            reconciliation_mode=discoveryengine_v1.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
        )
    )
    print(f"  operation: {op.operation.name}")
    print("  waiting for import to complete (typically 1-5 min)...")
    result = op.result(timeout=900)
    print("✓ Import complete.")
    print(f"  result: {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
