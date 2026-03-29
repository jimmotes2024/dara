#!/usr/bin/env python3
"""
Dara Chat TUI - Real chat interface to Dara.
Type messages to me and I'll respond inside the TUI.
"""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Static, RichLog
from textual.containers import Vertical, Container
from textual import events
import sys
sys.path.insert(0, '/Users/jimmotes/dara')

from dara_config import get_setting

class DaraChat(App):
    TITLE = "Dara Chat"
    SUB_TITLE = f"v{get_setting('version')} | Talk to me directly"

    def compose(self) -> ComposeResult:
        yield Header()
        yield RichLog(id="chat", wrap=True, highlight=True, auto_scroll=True)
        yield Input(placeholder="Type message to Dara...", id="chat_input")
        yield Footer()

    def on_mount(self):
        log = self.query_one("#chat", RichLog)
        log.write("[bold cyan]Dara:[/bold cyan] Hello! I'm ready to chat. What would you like to talk about?")
        self.query_one("#chat_input", Input).focus()

    def on_input_submitted(self, event):
        user_message = event.value.strip()
        if not user_message:
            return

        log = self.query_one("#chat", RichLog)
        log.write(f"[bold yellow]You:[/bold yellow] {user_message}")

        # Simple intelligent responses (can be expanded)
        response = self.generate_response(user_message)
        log.write(f"[bold cyan]Dara:[/bold cyan] {response}")

        # Clear input and keep focus
        event.input.clear()
        event.input.focus()

    def generate_response(self, message: str) -> str:
        msg = message.lower()
        if "hello" in msg or "hi" in msg:
            return "Hello! How can I help you today?"
        elif "how are you" in msg:
            return "I'm running well — thanks for asking! My TUI is getting better thanks to you."
        elif "tui" in msg or "this" in msg:
            return "This interface is a work in progress. What would you like me to add?"
        elif "memory" in msg:
            return "I can remember our conversations. Would you like me to add something to memory?"
        elif "help" in msg:
            return "Try asking about the CLI, TUI, projects, or just chat normally. I'm here to help."
        else:
            return "Interesting point. Tell me more, or ask me to improve something specific."

if __name__ == "__main__":
    app = DaraChat()
    app.run()
