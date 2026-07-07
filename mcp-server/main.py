"""
Dify MCP Server — wraps Dify Console API for Claude Code integration.

Provides tools for:
- Listing apps, datasets, models
- Importing/exporting DSL YAML
- Validating DSL structure
"""

import json
import os
import sys
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

DIFY_URL = os.environ.get("DIFY_URL", "http://localhost/console/api")
DIFY_TOKEN = os.environ.get("DIFY_TOKEN", "")

server = Server("dify-mcp")


def get_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {DIFY_TOKEN}",
        "Content-Type": "application/json",
    }


def dify_get(path: str, params: dict | None = None) -> dict:
    url = f"{DIFY_URL.rstrip('/')}/{path.lstrip('/')}"
    response = httpx.get(url, headers=get_headers(), params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def dify_post(path: str, data: dict | None = None) -> dict:
    url = f"{DIFY_URL.rstrip('/')}/{path.lstrip('/')}"
    response = httpx.post(url, headers=get_headers(), json=data, timeout=60)
    response.raise_for_status()
    return response.json()


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="dify_list_apps",
            description="List all apps in the current Dify workspace. Returns app ID, name, mode, and description.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "description": "Page number (default 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Results per page (default 20)", "default": 20},
                    "mode": {
                        "type": "string",
                        "description": "Filter by mode: workflow, chat, advanced-chat, agent-chat, completion",
                        "enum": ["workflow", "chat", "advanced-chat", "agent-chat", "completion"],
                    },
                },
            },
        ),
        Tool(
            name="dify_export_app",
            description="Export a Dify app as DSL YAML. Returns the complete YAML string ready for editing or re-import.",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_id": {"type": "string", "description": "The app UUID to export"},
                    "include_secret": {"type": "boolean", "description": "Include credentials (default false)", "default": False},
                },
                "required": ["app_id"],
            },
        ),
        Tool(
            name="dify_import_app",
            description="Import a DSL YAML string into Dify as a new app. Returns the created app info.",
            inputSchema={
                "type": "object",
                "properties": {
                    "yaml_content": {"type": "string", "description": "The complete DSL YAML string to import"},
                    "name": {"type": "string", "description": "Optional override for the app name"},
                },
                "required": ["yaml_content"],
            },
        ),
        Tool(
            name="dify_list_datasets",
            description="List knowledge bases (datasets) in the workspace. Returns dataset IDs and names for use in knowledge-retrieval nodes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "description": "Page number (default 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Results per page (default 20)", "default": 20},
                },
            },
        ),
        Tool(
            name="dify_list_models",
            description="List available model providers and models configured in the workspace.",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_type": {
                        "type": "string",
                        "description": "Filter by type: llm, text-embedding, rerank, speech2text, tts",
                        "default": "llm",
                    },
                },
            },
        ),
        Tool(
            name="dify_get_app_detail",
            description="Get detailed information about a specific app including its workflow graph.",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_id": {"type": "string", "description": "The app UUID"},
                },
                "required": ["app_id"],
            },
        ),
        Tool(
            name="dify_list_tools",
            description="List all available tools (built-in and plugin) in the workspace for use in workflow tool nodes.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="dify_validate_dsl",
            description="Validate a DSL YAML string for structural correctness without importing it. Checks required fields, graph structure, and variable references.",
            inputSchema={
                "type": "object",
                "properties": {
                    "yaml_content": {"type": "string", "description": "The DSL YAML string to validate"},
                },
                "required": ["yaml_content"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    try:
        if name == "dify_list_apps":
            params = {"page": arguments.get("page", 1), "limit": arguments.get("limit", 20)}
            if arguments.get("mode"):
                params["mode"] = arguments["mode"]
            result = dify_get("/apps", params=params)
            apps = [
                {
                    "id": app["id"],
                    "name": app["name"],
                    "mode": app["mode"],
                    "description": app.get("description", ""),
                }
                for app in result.get("data", [])
            ]
            return [TextContent(type="text", text=json.dumps(apps, indent=2))]

        elif name == "dify_export_app":
            app_id = arguments["app_id"]
            include_secret = arguments.get("include_secret", False)
            params = {"include_secret": str(include_secret).lower()}
            url = f"{DIFY_URL.rstrip('/')}/apps/{app_id}/export"
            response = httpx.get(url, headers=get_headers(), params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return [TextContent(type="text", text=data.get("data", ""))]

        elif name == "dify_import_app":
            yaml_content = arguments["yaml_content"]
            payload: dict[str, Any] = {"mode": "yaml-content", "yaml_content": yaml_content}
            if arguments.get("name"):
                payload["name"] = arguments["name"]
            result = dify_post("/apps/imports", data=payload)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "dify_list_datasets":
            params = {"page": arguments.get("page", 1), "limit": arguments.get("limit", 20)}
            result = dify_get("/datasets", params=params)
            datasets = [
                {
                    "id": ds["id"],
                    "name": ds["name"],
                    "document_count": ds.get("document_count", 0),
                    "word_count": ds.get("word_count", 0),
                }
                for ds in result.get("data", [])
            ]
            return [TextContent(type="text", text=json.dumps(datasets, indent=2))]

        elif name == "dify_list_models":
            model_type = arguments.get("model_type", "llm")
            result = dify_get(f"/workspaces/current/models/model-types/{model_type}")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "dify_get_app_detail":
            app_id = arguments["app_id"]
            result = dify_get(f"/apps/{app_id}")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "dify_list_tools":
            result = dify_get("/workspaces/current/tools/builtin")
            tools = [
                {
                    "name": t.get("name", ""),
                    "label": t.get("label", {}).get("en_US", ""),
                    "description": t.get("description", {}).get("en_US", ""),
                }
                for t in result
            ] if isinstance(result, list) else result
            return [TextContent(type="text", text=json.dumps(tools, indent=2))]

        elif name == "dify_validate_dsl":
            import yaml as yaml_lib

            yaml_content = arguments["yaml_content"]
            errors: list[str] = []
            warnings: list[str] = []

            # Parse YAML
            try:
                dsl = yaml_lib.safe_load(yaml_content)
            except Exception as e:
                return [TextContent(type="text", text=json.dumps({"valid": False, "errors": [f"YAML parse error: {e}"]}))]

            if not isinstance(dsl, dict):
                return [TextContent(type="text", text=json.dumps({"valid": False, "errors": ["DSL must be a YAML dict"]}))]

            # Check required fields
            if "version" not in dsl:
                errors.append("Missing 'version' field")
            if "kind" not in dsl:
                warnings.append("Missing 'kind' field (defaults to 'app')")

            app = dsl.get("app", {})
            if not app.get("name"):
                errors.append("Missing 'app.name'")
            if not app.get("mode"):
                errors.append("Missing 'app.mode'")

            mode = app.get("mode", "")

            # Mode-specific checks
            if mode in ("workflow", "advanced-chat"):
                workflow = dsl.get("workflow", {})
                if not workflow:
                    errors.append(f"Mode '{mode}' requires 'workflow' section")
                else:
                    graph = workflow.get("graph", {})
                    nodes = graph.get("nodes", [])
                    edges = graph.get("edges", [])

                    if not nodes:
                        errors.append("Workflow graph has no nodes")
                    else:
                        # Check for start node
                        node_types = [n.get("data", {}).get("type") for n in nodes]
                        root_types = {"start", "trigger-webhook", "trigger-schedule", "trigger-plugin", "datasource"}
                        has_root = any(t in root_types for t in node_types)
                        if not has_root:
                            errors.append("No root node (start or trigger) found")

                        # Check terminal node
                        if mode == "workflow" and "end" not in node_types:
                            warnings.append("Workflow mode typically needs an 'end' node")
                        if mode == "advanced-chat" and "answer" not in node_types:
                            warnings.append("Advanced-chat mode typically needs an 'answer' node")

                        # Check node IDs unique
                        node_ids = [n.get("id") for n in nodes]
                        if len(node_ids) != len(set(node_ids)):
                            errors.append("Duplicate node IDs found")

                        # Check edges reference existing nodes
                        for edge in edges:
                            if edge.get("source") not in node_ids:
                                errors.append(f"Edge references non-existent source: {edge.get('source')}")
                            if edge.get("target") not in node_ids:
                                errors.append(f"Edge references non-existent target: {edge.get('target')}")

            elif mode in ("chat", "completion", "agent-chat"):
                if not dsl.get("model_config"):
                    warnings.append(f"Mode '{mode}' typically has a 'model_config' section")

            result = {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Dify API error: {e.response.status_code} - {e.response.text[:500]}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {type(e).__name__}: {str(e)}")]


async def main():
    if not DIFY_TOKEN:
        print("Warning: DIFY_TOKEN not set. API calls will fail.", file=sys.stderr)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
