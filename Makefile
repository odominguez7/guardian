
# ==============================================================================
# Installation & Setup
# ==============================================================================

# Install dependencies using uv package manager
install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.8.13/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync

# ==============================================================================
# Playground Targets
# ==============================================================================

# Launch local dev playground
playground:
	@echo "==============================================================================="
	@echo "| 🚀 Starting your agent playground...                                        |"
	@echo "|                                                                             |"
	@echo "| 💡 Try asking: What's the weather in San Francisco?                         |"
	@echo "|                                                                             |"
	@echo "| 🔍 IMPORTANT: Select the 'app' folder to interact with your agent.          |"
	@echo "==============================================================================="
	uv run adk web . --port 8501 --reload_agents

# ==============================================================================
# Local Development Commands
# ==============================================================================

# Launch local development server with hot-reload
# Usage: make local-backend [PORT=8000] - Specify PORT for parallel scenario testing
local-backend:
	uv run uvicorn app.fast_api_app:app --host localhost --port $(or $(PORT),8000) --reload

# ==============================================================================
# A2A Protocol Inspector
# ==============================================================================

# Launch A2A Protocol Inspector to test your agent implementation
inspector: setup-inspector-if-needed build-inspector-if-needed
	@echo "==============================================================================="
	@echo "| 🔍 A2A Protocol Inspector                                                  |"
	@echo "==============================================================================="
	@echo "| 🌐 Inspector UI: http://localhost:5001                                     |"
	@echo "|                                                                             |"
	@echo "| 💡 Testing Locally:                                                         |"
	@echo "|    Paste this URL into the inspector:                                      |"
	@echo "|    http://localhost:8000/a2a/app/.well-known/agent-card.json              |"
	@echo "|                                                                             |"
	@echo "| 💡 Testing Remote Deployment:                                               |"
	@echo "|    <SERVICE_URL>/a2a/app/.well-known/agent-card.json"
	@echo "|    (Get SERVICE_URL from 'make deploy' output or Cloud Console)            |"
	@echo "|                                                                             |"
	@echo "|    🔐 Auth: Expand 'Authentication & Headers', select 'Bearer Token',       |"
	@echo "|       and paste output of: gcloud auth print-identity-token                |"
	@echo "==============================================================================="
	@echo ""
	cd tools/a2a-inspector/backend && uv run app.py

# Internal: Setup inspector if not already present (runs once)
# TODO: Update to --branch v1.0.0 when a2a-inspector publishes releases
setup-inspector-if-needed:
	@if [ ! -d "tools/a2a-inspector" ]; then \
		echo "" && \
		echo "📦 First-time setup: Installing A2A Inspector..." && \
		echo "" && \
		mkdir -p tools && \
		git clone --quiet https://github.com/a2aproject/a2a-inspector.git tools/a2a-inspector && \
		(cd tools/a2a-inspector && git -c advice.detachedHead=false checkout --quiet 893e4062f6fbd85a8369228ce862ebbf4a025694) && \
		echo "📥 Installing Python dependencies..." && \
		(cd tools/a2a-inspector && uv sync --quiet) && \
		echo "📥 Installing Node.js dependencies..." && \
		(cd tools/a2a-inspector/frontend && npm install --silent) && \
		echo "🔨 Building frontend..." && \
		(cd tools/a2a-inspector/frontend && npm run build --silent) && \
		echo "" && \
		echo "✅ A2A Inspector setup complete!" && \
		echo ""; \
	fi

# Internal: Build inspector frontend if needed
build-inspector-if-needed:
	@if [ -d "tools/a2a-inspector" ] && [ ! -f "tools/a2a-inspector/frontend/public/script.js" ]; then \
		echo "🔨 Building inspector frontend..."; \
		cd tools/a2a-inspector/frontend && npm run build; \
	fi

# ==============================================================================
# Backend Deployment Targets
# ==============================================================================

# Deploy the agent remotely
# Usage: make deploy [IAP=true] [PORT=8080] - Set IAP=true to enable Identity-Aware Proxy, PORT to specify container port
deploy:
	PROJECT_ID=$$(gcloud config get-value project) && \
	PROJECT_NUMBER=$$(gcloud projects describe $$PROJECT_ID --format="value(projectNumber)") && \
	gcloud beta run deploy guardian \
		--source . \
		--memory "4Gi" \
		--project $$PROJECT_ID \
		--region "us-central1" \
		--no-allow-unauthenticated \
		--no-cpu-throttling \
		--labels "created-by=adk" \
		--update-build-env-vars "AGENT_VERSION=$(shell awk -F'"' '/^version = / {print $$2}' pyproject.toml || echo '0.0.0')" \
		--update-env-vars \
		"APP_URL=https://guardian-$$PROJECT_NUMBER.us-central1.run.app,DATA_STORE_ID=guardian-collection_documents,DATA_STORE_REGION=global" \
		$(if $(IAP),--iap) \
		$(if $(PORT),--port=$(PORT))

# Alias for 'make deploy' for backward compatibility
backend: deploy

# ==============================================================================
# A2A Peer Deployment Targets
# ==============================================================================

# Deploy the Park Service peer agent as its own Cloud Run service.
# Two-step: Cloud Build builds the peer's Dockerfile with the repo as context,
# then Cloud Run pulls the image. Independent from `make deploy`.
# After deploy, copy the printed URL into the GUARDIAN orchestrator's
# PARK_SERVICE_URL env var with `make wire-park-service PARK_URL=...`.
deploy-park-service:
	PROJECT_ID=$$(gcloud config get-value project) && \
	COMMIT_SHA=$$(git rev-parse --short HEAD) && \
	gcloud builds submit . \
		--config peers/park_service/cloudbuild.yaml \
		--substitutions COMMIT_SHA=$$COMMIT_SHA \
		--project $$PROJECT_ID && \
	gcloud beta run deploy guardian-park-service \
		--image us-central1-docker.pkg.dev/$$PROJECT_ID/cloud-run-source-deploy/guardian-park-service:latest \
		--memory "2Gi" \
		--project $$PROJECT_ID \
		--region "us-central1" \
		--no-allow-unauthenticated \
		--no-cpu-throttling \
		--labels "created-by=adk,peer=park-service" \
		--update-env-vars "AGENT_VERSION=0.1.0"

# After deploy-park-service, point GUARDIAN at the new URL and redeploy.
# Usage: make wire-park-service PARK_URL=https://guardian-park-service-XXX.us-central1.run.app
wire-park-service:
	@if [ -z "$(PARK_URL)" ]; then echo "ERROR: set PARK_URL=https://..."; exit 1; fi
	PROJECT_ID=$$(gcloud config get-value project) && \
	gcloud beta run services update guardian \
		--region us-central1 \
		--project $$PROJECT_ID \
		--update-env-vars "PARK_SERVICE_URL=$(PARK_URL)"

# Deploy the Sponsor Sustainability peer agent as its own Cloud Run service.
# Same build-then-deploy two-step as park_service. After deploy, run
# `make wire-sponsor-sustainability SPONSOR_URL=https://...` to point
# GUARDIAN at it.
deploy-sponsor-sustainability:
	PROJECT_ID=$$(gcloud config get-value project) && \
	COMMIT_SHA=$$(git rev-parse --short HEAD) && \
	gcloud builds submit . \
		--config peers/sponsor_sustainability/cloudbuild.yaml \
		--substitutions COMMIT_SHA=$$COMMIT_SHA \
		--project $$PROJECT_ID && \
	gcloud beta run deploy guardian-sponsor-sustainability \
		--image us-central1-docker.pkg.dev/$$PROJECT_ID/cloud-run-source-deploy/guardian-sponsor-sustainability:latest \
		--memory "2Gi" \
		--project $$PROJECT_ID \
		--region "us-central1" \
		--no-allow-unauthenticated \
		--no-cpu-throttling \
		--labels "created-by=adk,peer=sponsor-sustainability" \
		--update-env-vars "AGENT_VERSION=0.1.0"

# Wire GUARDIAN to a deployed sponsor_sustainability peer URL.
wire-sponsor-sustainability:
	@if [ -z "$(SPONSOR_URL)" ]; then echo "ERROR: set SPONSOR_URL=https://..."; exit 1; fi
	PROJECT_ID=$$(gcloud config get-value project) && \
	gcloud beta run services update guardian \
		--region us-central1 \
		--project $$PROJECT_ID \
		--update-env-vars "SPONSOR_SUSTAINABILITY_URL=$(SPONSOR_URL)"

# ==============================================================================
# Data Ingestion (Vertex AI Search)
# ==============================================================================

# Set up Vertex AI Search datastore (GCS bucket, data connector, search engine)
setup-datastore:
	PROJECT_ID=$$(gcloud config get-value project) && \
	(cd deployment/terraform/dev && terraform init && \
	terraform apply --var-file vars/env.tfvars --var dev_project_id=$$PROJECT_ID --auto-approve \
		-target=google_discovery_engine_search_engine.search_engine_dev)

# Upload sample data and trigger initial sync
data-ingestion:
	PROJECT_ID=$$(gcloud config get-value project) && \
	DATA_STORE_REGION=$$(grep 'data_store_region' deployment/terraform/dev/vars/env.tfvars | sed 's/.*= *"//;s/".*//') && \
	gcloud storage cp sample_data/* gs://$$PROJECT_ID-guardian-docs/ && \
	uv run deployment/terraform/scripts/start_connector_run.py $$PROJECT_ID $$DATA_STORE_REGION guardian-collection --wait

# Trigger an on-demand sync for the GCS Data Connector
sync-data:
	PROJECT_ID=$$(gcloud config get-value project) && \
	DATA_STORE_REGION=$$(grep 'data_store_region' deployment/terraform/dev/vars/env.tfvars | sed 's/.*= *"//;s/".*//') && \
	uv run deployment/terraform/scripts/start_connector_run.py $$PROJECT_ID $$DATA_STORE_REGION guardian-collection --wait

# ==============================================================================
# Infrastructure Setup
# ==============================================================================

# Set up development environment resources using Terraform
setup-dev-env:
	PROJECT_ID=$$(gcloud config get-value project) && \
	(cd deployment/terraform/dev && terraform init && terraform apply --var-file vars/env.tfvars --var dev_project_id=$$PROJECT_ID --auto-approve)

# ==============================================================================
# Testing & Code Quality
# ==============================================================================

# Run unit and integration tests
test:
	uv sync --dev
	uv run pytest tests/unit && uv run pytest tests/integration

# ==============================================================================
# Agent Evaluation
# ==============================================================================

# Run agent evaluation using ADK eval
# Usage: make eval [EVALSET=tests/eval/evalsets/basic.evalset.json] [EVAL_CONFIG=tests/eval/eval_config.json]
eval:
	@echo "==============================================================================="
	@echo "| Running Agent Evaluation                                                    |"
	@echo "==============================================================================="
	uv sync --dev --extra eval
	uv run adk eval ./app $${EVALSET:-tests/eval/evalsets/basic.evalset.json} \
		$(if $(EVAL_CONFIG),--config_file_path=$(EVAL_CONFIG),$(if $(wildcard tests/eval/eval_config.json),--config_file_path=tests/eval/eval_config.json,))

# Run evaluation with all evalsets
eval-all:
	@echo "==============================================================================="
	@echo "| Running All Evalsets                                                        |"
	@echo "==============================================================================="
	@for evalset in tests/eval/evalsets/*.evalset.json; do \
		echo ""; \
		echo "▶ Running: $$evalset"; \
		$(MAKE) eval EVALSET=$$evalset || exit 1; \
	done
	@echo ""
	@echo "✅ All evalsets completed"

# Run code quality checks (codespell, ruff, ty)
lint:
	uv sync --dev --extra lint
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run ty check .

# ==============================================================================
# Gemini Enterprise Integration
# ==============================================================================

# Register the deployed agent to Gemini Enterprise
# Usage: make register-gemini-enterprise (interactive - will prompt for required details)
# For non-interactive use, set env vars: ID or GEMINI_ENTERPRISE_APP_ID (full GE resource name)
# Optional env vars: GEMINI_DISPLAY_NAME, GEMINI_DESCRIPTION, AGENT_CARD_URL
register-gemini-enterprise:
	@PROJECT_ID=$$(gcloud config get-value project 2>/dev/null) && \
	PROJECT_NUMBER=$$(gcloud projects describe $$PROJECT_ID --format="value(projectNumber)" 2>/dev/null) && \
	uvx agent-starter-pack@0.41.3 register-gemini-enterprise \
		--agent-card-url="https://guardian-$$PROJECT_NUMBER.us-central1.run.app/a2a/app/.well-known/agent-card.json" \
		--deployment-target="cloud_run" \
		--project-number="$$PROJECT_NUMBER"