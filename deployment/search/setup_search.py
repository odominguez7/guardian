"""GUARDIAN — provision the Vertex AI Search data store + search engine.

Run once to bootstrap. Idempotent: re-runs detect existing resources and skip
creation. Prints the data_store_id and search_engine_id you need to wire into
app/agent.py and Cloud Run env vars.

Usage:
    .venv/bin/python deployment/search/setup_search.py
"""

from __future__ import annotations

import sys
import time

import google.auth
from google.api_core.exceptions import AlreadyExists, NotFound
from google.cloud import discoveryengine_v1

# --- Config -------------------------------------------------------------------
LOCATION = "global"
COLLECTION = "default_collection"
DATA_STORE_ID = "guardian-collection"
SEARCH_ENGINE_ID = "guardian-search-dev"
DATA_STORE_DISPLAY = "GUARDIAN — conservation corpus"
SEARCH_ENGINE_DISPLAY = "GUARDIAN — search dev"


def main() -> int:
    _, project_id = google.auth.default()
    print(f"Project: {project_id}")

    parent = f"projects/{project_id}/locations/{LOCATION}/collections/{COLLECTION}"

    # 1. Data store
    ds_client = discoveryengine_v1.DataStoreServiceClient()
    data_store_name = f"{parent}/dataStores/{DATA_STORE_ID}"

    try:
        ds = ds_client.get_data_store(name=data_store_name)
        print(f"✓ Data store exists: {ds.name}")
    except NotFound:
        print(f"Creating data store '{DATA_STORE_ID}'...")
        op = ds_client.create_data_store(
            request=discoveryengine_v1.CreateDataStoreRequest(
                parent=parent,
                data_store=discoveryengine_v1.DataStore(
                    display_name=DATA_STORE_DISPLAY,
                    industry_vertical=discoveryengine_v1.IndustryVertical.GENERIC,
                    solution_types=[
                        discoveryengine_v1.SolutionType.SOLUTION_TYPE_SEARCH,
                    ],
                    content_config=discoveryengine_v1.DataStore.ContentConfig.CONTENT_REQUIRED,
                ),
                data_store_id=DATA_STORE_ID,
            )
        )
        print(f"  operation: {op.operation.name}")
        ds = op.result(timeout=300)
        print(f"✓ Data store created: {ds.name}")

    # 2. Search engine
    engine_client = discoveryengine_v1.EngineServiceClient()
    engine_name = f"{parent}/engines/{SEARCH_ENGINE_ID}"

    try:
        engine = engine_client.get_engine(name=engine_name)
        print(f"✓ Search engine exists: {engine.name}")
    except NotFound:
        print(f"Creating search engine '{SEARCH_ENGINE_ID}'...")
        op = engine_client.create_engine(
            request=discoveryengine_v1.CreateEngineRequest(
                parent=parent,
                engine=discoveryengine_v1.Engine(
                    display_name=SEARCH_ENGINE_DISPLAY,
                    solution_type=discoveryengine_v1.SolutionType.SOLUTION_TYPE_SEARCH,
                    industry_vertical=discoveryengine_v1.IndustryVertical.GENERIC,
                    data_store_ids=[DATA_STORE_ID],
                    search_engine_config=discoveryengine_v1.Engine.SearchEngineConfig(
                        search_tier=discoveryengine_v1.SearchTier.SEARCH_TIER_STANDARD,
                        search_add_ons=[discoveryengine_v1.SearchAddOn.SEARCH_ADD_ON_LLM],
                    ),
                ),
                engine_id=SEARCH_ENGINE_ID,
            )
        )
        print(f"  operation: {op.operation.name}")
        # Engine creation is async; wait for completion
        engine = op.result(timeout=600)
        print(f"✓ Search engine created: {engine.name}")

    print()
    print("===================================================================")
    print(f"  DATA_STORE_ID:       {DATA_STORE_ID}")
    print(f"  SEARCH_ENGINE_ID:    {SEARCH_ENGINE_ID}")
    print(f"  LOCATION:            {LOCATION}")
    print(f"  COLLECTION:          {COLLECTION}")
    print(f"  PROJECT:             {project_id}")
    print("===================================================================")
    print()
    print("Wire into Cloud Run env vars:")
    print(f"  DATA_STORE_ID={DATA_STORE_ID}")
    print(f"  DATA_STORE_REGION={LOCATION}")
    print()
    print("Next: .venv/bin/python deployment/search/ingest_corpus.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
