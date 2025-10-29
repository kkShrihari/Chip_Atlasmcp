"""
utils.py
Utility functions for Chip_Atlasmcp.
Provides helper methods for cleaning, summarizing, and displaying ChipAtlas data.
"""

from rich.console import Console
from rich.table import Table

console = Console()


def clean_text(text: str) -> str:
    """Clean and format text for display."""
    if not isinstance(text, str):
        return ""
    return text.strip().replace("\n", " ").replace("\r", "")


def summarize_response(data) -> str:
    """Generate a concise summary of a ChipAtlas API response or local data."""
    if not data:
        return "[red]No response data available.[/red]"

    try:
        # Handle dictionary
        if isinstance(data, dict):
            num_fields = len(data)
            sample_keys = ", ".join(list(data.keys())[:5])
            return f"[green]Response contains {num_fields} fields.[/green] Example keys: {sample_keys}"

        # Handle list of dictionaries
        if isinstance(data, list):
            if not data:
                return "[yellow]No entries found.[/yellow]"
            first = data[0]
            sample_keys = ", ".join(list(first.keys())[:5])
            return f"[green]Response contains {len(data)} records.[/green] Example fields: {sample_keys}"

        return "[red]Unsupported data format.[/red]"
    except Exception as e:
        return f"[red]Error summarizing response:[/red] {e}"


def display_response_table(data, max_rows: int = 10):
    """Display ChipAtlas data (dict or list of dicts) as a formatted Rich table."""
    if not data:
        console.print("[yellow]No data to display.[/yellow]")
        return

    # Handle list of dicts
    if isinstance(data, list):
        if not data:
            console.print("[yellow]No entries found.[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta")

        # Add headers from first row keys
        headers = list(data[0].keys())
        for header in headers:
            table.add_column(str(header), style="cyan", no_wrap=True)

        # Add rows
        for i, row in enumerate(data):
            if i >= max_rows:
                break
            values = [str(row.get(h, ""))[:77] + "..." if len(str(row.get(h, ""))) > 80 else str(row.get(h, "")) for h in headers]
            table.add_row(*values)

        console.print(table)
        return

    # Handle single dict
    if isinstance(data, dict):
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")

        for i, (key, value) in enumerate(data.items()):
            if i >= max_rows:
                break
            formatted_value = str(value)
            if len(formatted_value) > 80:
                formatted_value = formatted_value[:77] + "..."
            table.add_row(str(key), formatted_value)

        console.print(table)
        return

    console.print("[red]Cannot display data: expected a dictionary or list of dictionaries.[/red]")


#https://ccb-compute.cs.uni-saarland.de/mirtargetlink2