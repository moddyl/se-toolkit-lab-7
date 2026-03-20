"""Basic command handlers for the bot."""

def start_handler() -> str:
    """Handle /start command."""
    return "Hello! I'm your LMS Bot.\nAvailable commands:\n/start - Start the bot\n/help - Show help\n/health - Check backend status"

def help_handler() -> str:
    """Handle /help command."""
    return "Available commands:\n/start - Start the bot\n/help - Show this help\n/health - Check backend status\n/labs - List all labs (coming soon)"

def health_handler() -> str:
    """Handle /health command."""
    return "✅ Backend is healthy (placeholder)"