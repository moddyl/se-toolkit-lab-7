import sys
import httpx
import json
from config import LLM_API_KEY, LLM_API_BASE_URL, LLM_API_MODEL
from services.lms_client import (
    get_items, get_pass_rates, get_learners,
    get_scores, get_timeline, get_groups,
    get_top_learners, get_completion_rate, trigger_sync,
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get the list of all labs and tasks available in the LMS",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get the list of enrolled students and their groups",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day over time for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group scores and student counts for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-02'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-03'"},
                    "limit": {"type": "integer", "description": "Number of top learners to return, default 5"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get the completion rate percentage for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL pipeline sync to refresh data from the autochecker",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

SYSTEM_PROMPT = """You are SE Toolkit Bot — a data assistant for a software engineering course LMS.
You have access to tools that fetch real data from the backend.
Always use tools to answer questions about labs, students, scores, and pass rates.
Never guess data — always call a tool first.
Respond concisely and format data clearly for Telegram messages."""


def _execute_tool(name: str, args: dict) -> str:
    try:
        if name == "get_items":
            data = get_items()
            return json.dumps(data)
        elif name == "get_learners":
            data = get_learners()
            return json.dumps(data)
        elif name == "get_scores":
            data = get_scores(args["lab"])
            return json.dumps(data)
        elif name == "get_pass_rates":
            data = get_pass_rates(args["lab"])
            return json.dumps(data)
        elif name == "get_timeline":
            data = get_timeline(args["lab"])
            return json.dumps(data)
        elif name == "get_groups":
            data = get_groups(args["lab"])
            return json.dumps(data)
        elif name == "get_top_learners":
            data = get_top_learners(args["lab"], args.get("limit", 5))
            return json.dumps(data)
        elif name == "get_completion_rate":
            data = get_completion_rate(args["lab"])
            return json.dumps(data)
        elif name == "trigger_sync":
            data = trigger_sync()
            return json.dumps(data)
        else:
            return json.dumps({"error": f"Unknown tool: {name}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def route(user_message: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    with httpx.Client(timeout=60) as client:
        for _ in range(10):  # max iterations
            response = client.post(
                f"{LLM_API_BASE_URL}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {LLM_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": LLM_API_MODEL,
                    "messages": messages,
                    "tools": TOOLS,
                    "tool_choice": "auto",
                    "max_tokens": 1000,
                },
            )

            if response.status_code != 200:
                return f"❌ LLM error: HTTP {response.status_code} {response.text[:200]}"

            data = response.json()
            choice = data["choices"][0]
            msg = choice["message"]
            finish_reason = choice["finish_reason"]

            messages.append(msg)

            if finish_reason == "tool_calls" or (finish_reason == "stop" and msg.get("tool_calls")):
                tool_calls = msg.get("tool_calls", [])
                for tc in tool_calls:
                    name = tc["function"]["name"]
                    args = json.loads(tc["function"]["arguments"] or "{}")
                    print(f"[tool] LLM called: {name}({args})", file=sys.stderr)
                    result = _execute_tool(name, args)
                    result_preview = json.loads(result)
                    if isinstance(result_preview, list):
                        print(f"[tool] Result: {len(result_preview)} items", file=sys.stderr)
                    else:
                        print(f"[tool] Result: {str(result_preview)[:100]}", file=sys.stderr)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": result,
                    })
                print(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM", file=sys.stderr)
            else:
                return msg.get("content", "No response from LLM.")

    return "❌ LLM did not produce a final answer after maximum iterations."