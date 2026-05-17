# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# v8 Day 3-4 note: package __init__ deliberately empty.
# Originally re-exported `from .agent import app`, which fired Cloud Run
# root_agent construction on every `app.*` import and prevented the
# Agent Engine variant from claiming the same specialist instances
# (ADK's one-parent-per-agent rule). Day 3 deploy is now live at
# reasoningEngines/7109983694676295680.
#
# Callers that need the constructed FastAPI `app`:
#   from app.agent import app
#
# Callers that need root_agent for adk eval:
#   from app.agent import root_agent
#
# This keeps Cloud Run + Agent Engine + adk eval mutually compatible.
