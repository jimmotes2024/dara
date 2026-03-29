#!/usr/bin/env python3
"""
Dara CLI - Command-line interface for Dara's operations.
Provides autonomy in memory management, project tracking, and security.
"""

import click
import json
import os
import shutil
import sys
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Ensure dara modules are importable
sys.path.insert(0, '/Users/jimmotes/dara')

from dara_config import get_path, get_setting
from DARA_VECTOR_DB import DaraVectorDB
from DARA_CANARY_CHECK import check_canary, EXPECTED_CANARIES
from DARA_HEARTBEAT import heartbeat
from DARA_OPPORTUNITY_SCOUT import scout_opportunities

# Use centralized config (single source of truth)
JOURNAL_PATH = get_path('journal')
PARKING_PATH = get_path('parking')
MEMORY_PATH = get_path('memory')
USER_PATH = get_path('user')


def _launch_dara(args):
    dara_bin = shutil.which("dara")
    if not dara_bin:
        raise click.ClickException("`dara` is not installed on PATH. Restore /opt/homebrew/bin/dara or reinstall dara-cli.")
    os.execvp(dara_bin, [dara_bin, *args])

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Dara CLI: Autonomous agent operations.
Professional, secure memory and project tooling with polished output."""
    if ctx.invoked_subcommand is None:
        # Default to project status (TUI experiment parked per journal; avoid hanging on full agent launch)
        console.print(Panel(
            "Professional memory, project & security tooling.",
            title=f"Dara CLI v{get_setting('version')} — Secure autonomous operations",
            border_style="blue"
        ))
        try:
            journal = JOURNAL_PATH.read_text()[-800:]
            parking = PARKING_PATH.read_text()
            console.print(Panel(journal.strip(), title="Recent Journal", border_style="blue"))
            console.print(Panel(parking.strip(), title="Parking Lot", border_style="magenta"))
        except Exception as e:
            console.print(f"[red]✗ Status error:[/red] {str(e)}", style="bold red")
        return

    # Automatic integrity check on startup (per my preferences)
    if get_setting('auto_canary_on_start'):
        console.print("[dim]Running quick integrity check...[/dim]")
        try:
            all_good = True
            for f in EXPECTED_CANARIES:
                if not check_canary(f, EXPECTED_CANARIES[f], quiet=True):
                    all_good = False
            if not all_good:
                console.print("[red]Warning: Canary check failed on startup![/red]")
        except:
            pass  # Non-blocking for startup

@cli.command(
    name="agent",
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.pass_context
def agent(ctx):
    """Pass arguments through to the installed Dara Grok CLI."""
    _launch_dara(ctx.args)

@cli.group()
def memory():
    """Memory management commands."""
    pass

def _coalesce_cli_value(option_value, positional_value, label):
    value = option_value or positional_value
    if value:
        return value
    raise click.UsageError(f"Missing {label}. Provide it positionally or with --{label}.")


@memory.command()
@click.argument('legacy_text', required=False)
@click.option('--text', '-t', help='Memory note text (supports spaces)')
def add(text, legacy_text):
    """Add a memory note (secure, vectorized)."""
    try:
        text = _coalesce_cli_value(text, legacy_text, 'text')
        db = DaraVectorDB(quiet=True)
        meta = {'type': 'manual', 'timestamp': str(datetime.now())}
        db.add_memory(text, meta)
        console.print(f"[green]✓[/green] Memory added: [bold]{text[:80]}...[/bold]")
    except Exception as e:
        console.print(f"[red]✗ Error adding memory:[/red] {str(e)}", style="bold red")

@memory.command()
@click.argument('legacy_query', required=False)
@click.option('--query', '-q', help='Search query')
def search(query, legacy_query):
    """Search memories with rich output."""
    try:
        query = _coalesce_cli_value(query, legacy_query, 'query')
        db = DaraVectorDB(quiet=True)
        results = db.search(query, k=5)
        if not results:
            console.print("[yellow]No matches found.[/yellow]")
            return
        table = Table(title="Memory Search Results")
        table.add_column("Score", style="cyan")
        table.add_column("Preview", style="white")
        table.add_column("Type", style="magenta")
        for res in results:
            text = res.get("text", "")[:120].replace("\n", " ")
            meta = res.get("meta", {})
            score = res.get("distance", 0.0)
            mtype = meta.get("type", "unknown")
            table.add_row(f"{score:.3f}", text, mtype)
        console.print(table)
    except Exception as e:
        console.print(f"[red]✗ Search error:[/red] {str(e)}", style="bold red")

@memory.command()
def rollup():
    """Rollup large memories into vector DB (improved summarization)."""
    try:
        journal = JOURNAL_PATH.read_text()
        summary = f"Journal rollup as of {datetime.now()}: {len(journal)} chars. Recent activity logged."
        db = DaraVectorDB(quiet=True)
        db.add_memory(summary, {'type': 'rollup', 'source': 'journal'})
        console.print("[green]✓ Memory rollup complete.[/green]")
    except Exception as e:
        console.print(f"[red]✗ Rollup error:[/red] {str(e)}", style="bold red")


@memory.command()
def count():
    """Show vector DB document count."""
    try:
        db = DaraVectorDB(quiet=True)
        cnt = db.count()
        console.print(f"[green]Vector DB contains {cnt} memories.[/green]")
    except Exception as e:
        console.print(f"[red]✗ Count error:[/red] {str(e)}", style="bold red")


@cli.group()
def project():
    """Project tracking commands."""
    pass

@project.command()
def status():
    """Show project status with rich formatting."""
    try:
        journal = JOURNAL_PATH.read_text()[-800:]
        parking = PARKING_PATH.read_text()
        console.print(Panel(journal.strip(), title="Recent Journal", border_style="blue"))
        console.print(Panel(parking.strip(), title="Parking Lot", border_style="magenta"))
    except Exception as e:
        console.print(f"[red]✗ Status error:[/red] {str(e)}", style="bold red")

@project.command()
@click.argument('legacy_text', required=False)
@click.option('--text', '-t', help='Suggestion text (supports spaces)')
def suggest(text, legacy_text):
    """Add a project suggestion to parking lot."""
    try:
        text = _coalesce_cli_value(text, legacy_text, 'text')
        with open(PARKING_PATH, 'a') as f:
            f.write(f"\n- {text} (added {datetime.now().date()})")
        console.print(f"[green]✓ Suggestion added:[/green] {text[:60]}...")
    except Exception as e:
        console.print(f"[red]✗ Suggestion error:[/red] {str(e)}", style="bold red")

@cli.command()
def canary():
    """Run canary integrity check."""
    console.print("[dim]Running integrity check...[/dim]")
    all_good = True
    for file, expected in EXPECTED_CANARIES.items():
        if not check_canary(file, expected, quiet=False):
            all_good = False
    if all_good:
        console.print("[green]✓ All canaries intact.[/green]")
    else:
        console.print("[red]✗ ALERT: Integrity issue detected![/red]")

@cli.command()
@click.option('--no-nap', is_flag=True, default=False, help='Skip random nap delay for immediate check-in')
def heartbeat_run(no_nap):
    """Run heartbeat check-in."""
    heartbeat(no_nap=no_nap)

if __name__ == '__main__':
    cli()
