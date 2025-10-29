"""
cli.py
Command-line interface for the Chip_Atlasmcp package.
"""

import typer
from rich.console import Console
from Chip_Atlasmcp import Chip_Atlasmcp

app = typer.Typer(help="CLI for retrieving and summarizing data from ChipAtlas.")
console = Console()


@app.command()
def fetch(
    gene: str,
    metadata_type: str = typer.Option(
        "experiment_list",
        help=(
            "Type of metadata to fetch: "
            "experiment_list, file_list, analysis_list, antigen_list, or celltype_list."
        ),
    ),
):
    """
    Fetch and display ChIP-Atlas data for a specified gene or antigen.
    Displays full details in the terminal and saves the complete dataset
    (including all metadata and links) in the results folder.
    """
    console.print(f"[bold cyan]Retrieving ChipAtlas {metadata_type} data for:[/bold cyan] {gene}")

    try:
        # Fetch and display the data (main output comes from Chip_Atlasmcp.py)
        data = Chip_Atlasmcp.fetch_and_display(metadata_type, gene)

        if data is None or (hasattr(data, "empty") and data.empty):
            console.print(f"[yellow]No data found for gene: {gene} in {metadata_type}[/yellow]")
            raise typer.Exit(code=1)

        # Save the full dataset (all metadata and links)
        Chip_Atlasmcp.save_full_dataset(data, gene, metadata_type)

        console.print(
            f"\n[green]Full dataset (including all records and metadata) saved under results/chip_atlas_{gene}_{metadata_type}.csv[/green]\n"
        )

    except Exception as e:
        console.print(f"[red]Error while fetching or displaying data:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def version():
    """Display Chip_Atlasmcp version and author information."""
    try:
        from Chip_Atlasmcp import __version__, __author__
        console.print(
            f"Chip_Atlasmcp version {__version__} by {__author__}"
        )
    except ImportError:
        console.print("Chip_Atlasmcp version 0.1.0 by Shrihari")





# """
# cli.py
# Command-line interface for the Chip_Atlasmcp package.
# """

# import typer
# from rich.console import Console
# from rich.table import Table
# from Chip_Atlasmcp import Chip_Atlasmcp

# app = typer.Typer(help="CLI for retrieving and summarizing data from ChipAtlas.")
# console = Console()


# @app.command()
# def fetch(
#     gene: str,
#     metadata_type: str = typer.Option(
#         "experiment_list",
#         help=(
#             "Type of metadata to fetch: "
#             "experiment_list, file_list, analysis_list, antigen_list, or celltype_list."
#         ),
#     ),
# ):
#     """
#     Fetch and display ChIP-Atlas data for a specified gene or antigen.
#     Displays key information in the terminal and saves the complete dataset
#     (including all metadata and links) in the results folder.
#     """
#     console.print(f"[bold cyan]Retrieving ChipAtlas {metadata_type} data for:[/bold cyan] {gene}")

#     try:
#         data = Chip_Atlasmcp.fetch_and_display(metadata_type, gene)

#         if data is None or (hasattr(data, "empty") and data.empty):
#             console.print(f"[yellow]No data found for gene: {gene} in {metadata_type}[/yellow]")
#             raise typer.Exit(code=1)

#         # Display a concise preview (top 25 rows)
#         console.print("\n[bold green]Displaying top 25 essential results:[/bold green]\n")
#         table = Table(show_header=True, header_style="bold magenta")

#         essential_columns = [
#             "Experimental ID", "Antigen", "Cell type", "Genome assembly", "Title"
#         ]
#         available_columns = [col for col in essential_columns if col in data.columns]
#         for col in available_columns:
#             table.add_column(col, justify="center", overflow="fold")

#         for _, row in data.head(25).iterrows():
#             table.add_row(*[str(row.get(col, "N/A")) for col in available_columns])

#         console.print(table)

#         # Save the full dataset
#         Chip_Atlasmcp.save_full_dataset(data, gene, metadata_type)

#         console.print(
#             f"\n[green]Full dataset (including all records and metadata) saved under results/chip_atlas_{gene}_{metadata_type}.csv[/green]\n"
#         )

#     except Exception as e:
#         console.print(f"[red]Error while fetching or displaying data:[/red] {e}")
#         raise typer.Exit(code=1)


# @app.command()
# def version():
#     """Display Chip_Atlasmcp version and author information."""
#     try:
#         from Chip_Atlasmcp import __version__, __author__
#         console.print(
#             f"Chip_Atlasmcp version {__version__} by {__author__}"
#         )
#     except ImportError:
#         console.print("Chip_Atlasmcp version 0.1.0 by Shrihari")

