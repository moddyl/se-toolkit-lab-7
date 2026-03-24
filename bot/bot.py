import os
import sys
import asyncio
import httpx
from dotenv import load_dotenv

# Load environment variables
_base = os.path.join(os.path.dirname(__file__), '..')
load_dotenv(dotenv_path=os.path.join(_base, '.env.docker.secret'))
load_dotenv(dotenv_path=os.path.join(_base, '.env.bot.secret'))
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:42002")
LMS_API_KEY = os.getenv("LMS_API_KEY") or os.getenv("API_KEY")

BOT_NAME = "LMS Assistant Bot"


def get_headers():
    return {"Authorization": f"Bearer {LMS_API_KEY}"}


# ── Command handlers ──────────────────────────────────────────────────────────

def handle_start() -> str:
    return (
        f"👋 Welcome to {BOT_NAME}!\n\n"
        "I can help you check lab scores, view available labs, "
        "and monitor the backend status.\n\n"
        "Type /help to see all available commands."
    )


def handle_help() -> str:
    return (
        "📚 Available commands:\n\n"
        "/start — Welcome message\n"
        "/help — Show this help message\n"
        "/health — Check backend status\n"
        "/labs — List all available labs\n"
        "/scores <lab> — Show pass rates for a lab (e.g. /scores lab-04)"
    )


def handle_health() -> str:
    try:
        response = httpx.get(
            f"{BACKEND_URL}/items/",
            headers=get_headers(),
            timeout=5.0
        )
        response.raise_for_status()
        items = response.json()
        count = len(items)
        return f"✅ Backend is healthy. {count} items available."
    except httpx.ConnectError:
        host = BACKEND_URL.replace("http://", "").replace("https://", "")
        return f"❌ Backend error: connection refused ({host}). Check that the services are running."
    except httpx.TimeoutException:
        return f"❌ Backend error: request timed out ({BACKEND_URL}). The service may be overloaded."
    except httpx.HTTPStatusError as e:
        return f"❌ Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except Exception as e:
        return f"❌ Backend error: {e}"


def handle_labs() -> str:
    try:
        response = httpx.get(
            f"{BACKEND_URL}/items/",
            headers=get_headers(),
            timeout=5.0
        )
        response.raise_for_status()
        items = response.json()

        # Filter only lab items
        labs = [
            item for item in items
            if item.get("type") == "lab" or item.get("item_type") == "lab"
        ]

        # Fallback: items with lab-like IDs
        if not labs:
            labs = [
                item for item in items
                if str(item.get("id", "")).startswith("lab-")
                or str(item.get("lab_id", "")).startswith("lab-")
            ]

        if not labs:
            return "No labs found in the backend."

        lines = ["📋 Available labs:"]
        for lab in labs:
            name = lab.get("name") or lab.get("title") or lab.get("id") or "Unknown"
            lab_id = lab.get("id") or lab.get("lab_id") or ""
            if lab_id and lab_id != name:
                lines.append(f"- {lab_id} — {name}")
            else:
                lines.append(f"- {name}")

        return "\n".join(lines)

    except httpx.ConnectError:
        host = BACKEND_URL.replace("http://", "").replace("https://", "")
        return f"❌ Backend error: connection refused ({host}). Check that the services are running."
    except httpx.TimeoutException:
        return f"❌ Backend error: request timed out ({BACKEND_URL})."
    except httpx.HTTPStatusError as e:
        return f"❌ Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}."
    except Exception as e:
        return f"❌ Backend error: {e}"


def handle_scores(args: str) -> str:
    lab = args.strip()

    if not lab:
        return (
            "⚠️ Please specify a lab. Usage: /scores <lab>\n"
            "Example: /scores lab-04"
        )

    try:
        response = httpx.get(
            f"{BACKEND_URL}/analytics/pass-rates",
            params={"lab": lab},
            headers=get_headers(),
            timeout=5.0
        )
        response.raise_for_status()
        data = response.json()

        if not data:
            return f"No score data found for {lab}. Make sure the lab ID is correct."

        tasks = data if isinstance(data, list) else data.get("tasks", [])

        if not tasks:
            return f"No task data found for {lab}."

        lines = [f"📊 Pass rates for {lab.upper().replace('-', ' ')}:"]
        for task in tasks:
            name = task.get("task_name") or task.get("name") or task.get("title") or "Unknown task"
            rate = task.get("pass_rate") or task.get("rate") or 0
            attempts = task.get("attempts") or task.get("total") or 0

            rate_pct = f"{float(rate) * 100:.1f}%" if float(rate) <= 1 else f"{float(rate):.1f}%"

            if attempts:
                lines.append(f"- {name}: {rate_pct} ({attempts} attempts)")
            else:
                lines.append(f"- {name}: {rate_pct}")

        return "\n".join(lines)

    except httpx.ConnectError:
        host = BACKEND_URL.replace("http://", "").replace("https://", "")
        return f"❌ Backend error: connection refused ({host}). Check that the services are running."
    except httpx.TimeoutException:
        return f"❌ Backend error: request timed out ({BACKEND_URL})."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"⚠️ Lab '{lab}' not found. Check the lab ID with /labs."
        return f"❌ Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}."
    except Exception as e:
        return f"❌ Backend error: {e}"


def handle_unknown(command: str) -> str:
    return (
        f"❓ Unknown command: {command}\n"
        "Type /help to see all available commands."
    )


# ── Router ────────────────────────────────────────────────────────────────────

def process_command(text: str) -> str:
    text = text.strip()
    parts = text.split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if command == "/start":
        return handle_start()
    elif command == "/help":
        return handle_help()
    elif command == "/health":
        return handle_health()
    elif command == "/labs":
        return handle_labs()
    elif command == "/scores":
        return handle_scores(args)
    else:
        return handle_unknown(command)


# ── Test mode ─────────────────────────────────────────────────────────────────

def run_test(command: str):
    print(process_command(command))


# ── Telegram mode ─────────────────────────────────────────────────────────────

async def run_telegram():
    try:
        from telegram import Update
        from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
    except ImportError:
        print("python-telegram-bot not installed. Run: uv add python-telegram-bot")
        sys.exit(1)

    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set in environment.")
        sys.exit(1)

    async def telegram_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text or ""
        response = process_command(text)
        await update.message.reply_text(response)

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    for cmd in ["start", "help", "health", "labs", "scores"]:
        app.add_handler(CommandHandler(cmd, telegram_handler))

    app.add_handler(MessageHandler(filters.COMMAND, telegram_handler))

    print(f"{BOT_NAME} is running...")
    await app.run_polling()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--test":
        run_test(sys.argv[2])
    elif len(sys.argv) >= 2 and sys.argv[1] == "--test":
        print("Usage: uv run bot.py --test \"/command\"")
    else:
        asyncio.run(run_telegram())