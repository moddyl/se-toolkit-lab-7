import httpx
from services.lms_client import get_items, get_pass_rates


def handle_start() -> str:
    return (
        "👋 Welcome to SE Toolkit Bot!\n"
        "I help you track lab progress and scores.\n"
        "Use /help to see available commands."
    )


def handle_help() -> str:
    return (
        "Available commands:\n"
        "/start — welcome message\n"
        "/help — this help\n"
        "/health — check backend status\n"
        "/labs — list available labs\n"
        "/scores <lab> — per-task pass rates (e.g. /scores lab-04)"
    )


def handle_health() -> str:
    try:
        items = get_items()
        return f"✅ Backend is healthy. {len(items)} items available."
    except httpx.ConnectError as e:
        return f"❌ Backend error: connection refused ({e}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"❌ Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except Exception as e:
        return f"❌ Backend error: {e}"


def handle_labs() -> str:
    try:
        items = get_items()
        labs = [i for i in items if i.get("type") == "lab"]
        if not labs:
            # fallback: try items that look like labs by name/id
            labs = [i for i in items if "lab" in str(i.get("id", "")).lower()]
        if not labs:
            return "No labs found. The backend may have no data yet."
        lines = ["Available labs:"]
        for lab in labs:
            name = lab.get("name") or lab.get("title") or lab.get("id")
            lines.append(f"- {name}")
        return "\n".join(lines)
    except httpx.ConnectError as e:
        return f"❌ Backend error: connection refused ({e}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"❌ Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}."
    except Exception as e:
        return f"❌ Backend error: {e}"


def handle_scores(args: str) -> str:
    lab = args.strip()
    if not lab:
        return "Usage: /scores <lab-id>\nExample: /scores lab-04"
    try:
        data = get_pass_rates(lab)
        if not data:
            return f"No data found for '{lab}'. Check the lab ID."
        lines = [f"Pass rates for {lab}:"]
        for entry in data:
            task = entry.get("task") or entry.get("name") or entry.get("id") or "Unknown"
            rate = entry.get("avg_score")
            attempts = entry.get("attempts") or entry.get("total") or ""
            if rate is not None:
                pct = f"{float(rate):.1f}%"
                line = f"- {task}: {pct}"
                if attempts:
                    line += f" ({attempts} attempts)"
                lines.append(line)
            else:
                lines.append(f"- {task}: no data")
        return "\n".join(lines)
    except httpx.ConnectError as e:
        return f"❌ Backend error: connection refused ({e}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"❌ Lab '{lab}' not found. Use /labs to see available labs."
        return f"❌ Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}."
    except Exception as e:
        return f"❌ Backend error: {e}"


def handle_unknown(text: str) -> str:
    return f"❓ Unknown command: '{text}'\nUse /help to see available commands."