"""
chip_Atlasmcp.py
Full extended module for retrieving and processing data from the ChIP-Atlas database.

Features:
- Supports all 5 metadata types (experiment, file, analysis, antigen, celltype)
- Automatically downloads and extracts files if missing
- Handles TSV or CSV formats automatically
- Filters by user-provided keyword (gene, antigen, or cell type)
- Displays top 25–50 entries neatly in console
- Saves full results with all metadata fields as CSV
"""

import os
import zipfile
import requests
import pandas as pd
from io import BytesIO
from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table

console = Console()

# -----------------------
# 1️⃣ Metadata URLs
# -----------------------
METADATA_SPECS = {
    "experiment_list": {
        "filename": "chip_atlas_experiment_list.zip",
        "url": "https://dbarchive.biosciencedbc.jp/data/chip-atlas/LATEST/chip_atlas_experiment_list.zip",
        "unzipped_files": ["chip_atlas_experiment_list.tsv", "chip_atlas_experiment_list.csv"],
    },
    "file_list": {
        "filename": "chip_atlas_file_list.zip",
        "url": "https://dbarchive.biosciencedbc.jp/data/chip-atlas/LATEST/chip_atlas_file_list.zip",
        "unzipped_files": ["chip_atlas_file_list.tsv", "chip_atlas_file_list.csv"],
    },
    "analysis_list": {
        "filename": "chip_atlas_analysis_list.zip",
        "url": "https://dbarchive.biosciencedbc.jp/data/chip-atlas/LATEST/chip_atlas_analysis_list.zip",
        "unzipped_files": ["chip_atlas_analysis_list.tsv", "chip_atlas_analysis_list.csv"],
    },
    "antigen_list": {
        "filename": "chip_atlas_antigen_list.zip",
        "url": "https://dbarchive.biosciencedbc.jp/data/chip-atlas/LATEST/chip_atlas_antigen_list.zip",
        "unzipped_files": ["chip_atlas_antigen_list.tsv", "chip_atlas_antigen_list.csv"],
    },
    "celltype_list": {
        "filename": "chip_atlas_celltype_list.zip",
        "url": "https://dbarchive.biosciencedbc.jp/data/chip-atlas/LATEST/chip_atlas_celltype_list.zip",
        "unzipped_files": ["chip_atlas_celltype_list.tsv", "chip_atlas_celltype_list.csv"],
    },
}


# -----------------------
# 2️⃣ Ensure file exists or download
# -----------------------
def ensure_metadata_file(metadata_type: str, silent: bool = False) -> Optional[str]:
    """Ensure the metadata file exists locally, download if missing."""
    if metadata_type not in METADATA_SPECS:
        if not silent:
            console.print(f"[red]Unknown metadata type: {metadata_type}[/red]")
        return None

    spec = METADATA_SPECS[metadata_type]
    base_dir = os.path.expanduser("~/Chip_Atlasmcp")
    os.makedirs(base_dir, exist_ok=True)

    # Check if file already present
    for fname in spec["unzipped_files"]:
        fpath = os.path.join(base_dir, fname)
        if os.path.exists(fpath):
            if not silent:
                console.print(f"[green]Found local file for {metadata_type}:[/green] {fpath}")
            return fpath

    # Download otherwise
    if not silent:
        console.print(f"[yellow]Downloading {metadata_type} from {spec['url']}...[/yellow]")
    try:
        r = requests.get(spec["url"], timeout=60)
        r.raise_for_status()
        with zipfile.ZipFile(BytesIO(r.content)) as zf:
            zf.extractall(base_dir)
        if not silent:
            console.print(f"[green]Extracted {metadata_type} into:[/green] {base_dir}")
    except Exception as e:
        if not silent:
            console.print(f"[red]Error downloading/extracting {metadata_type}:[/red] {e}")
        return None

    # Verify extracted file exists
    for fname in spec["unzipped_files"]:
        fpath = os.path.join(base_dir, fname)
        if os.path.exists(fpath):
            return fpath

    if not silent:
        console.print(f"[red]Error: could not locate {metadata_type} file after extraction.[/red]")
    return None


# -----------------------
# 3️⃣ Load metadata safely
# -----------------------
def load_metadata(metadata_type: str, silent: bool = False) -> Optional[pd.DataFrame]:
    """Load a metadata table into a pandas DataFrame."""
    fpath = ensure_metadata_file(metadata_type, silent=silent)
    if not fpath:
        return None

    try:
        sep = "\t" if fpath.endswith(".tsv") else None
        df = pd.read_csv(fpath, sep=sep, dtype=str, encoding="utf-8", engine="python")
        if df.shape[1] == 1:
            df = pd.read_csv(fpath, sep=",", dtype=str, encoding="utf-8", engine="python")
    except UnicodeDecodeError:
        df = pd.read_csv(fpath, sep=sep, dtype=str, encoding="latin1", engine="python")
        if df.shape[1] == 1:
            df = pd.read_csv(fpath, sep=",", dtype=str, encoding="latin1", engine="python")
    except Exception as e:
        if not silent:
            console.print(f"[red]Error loading {metadata_type} file:[/red] {e}")
        return None

    df.columns = [c.strip() for c in df.columns]
    if not silent:
        console.print(f"[cyan]Loaded columns:[/cyan] {list(df.columns)}")
    return df


# -----------------------
# 4️⃣ Fetch, filter, display, save
# -----------------------
def fetch_and_display(metadata_type: str, keyword: str, column_hint: str = "Antigen", silent: bool = False):
    """Fetch and display entries from the chosen metadata list filtered by keyword."""
    df = load_metadata(metadata_type, silent=silent)
    if df is None:
        return None

    # --- Smart column detection ---
    col = None
    for c in df.columns:
        if c.strip().lower() == "antigen":
            col = c
            break
    if not col:
        possible_cols = [c for c in df.columns if "antigen" in c.lower()]
        if possible_cols:
            col = sorted(possible_cols, key=len)[0]

    if not col and "Cell type" in df.columns:
        col = "Cell type"

    if not col:
        if not silent:
            console.print(f"[red]No suitable column found in {metadata_type}[/red]")
        return None

    if not silent:
        console.print(f"[green]Using column:[/green] {col}")

    # --- Search keyword (case-insensitive) ---
    matches = df[df[col].astype(str).str.contains(keyword, case=False, na=False)]
    if matches.empty:
        if not silent:
            console.print(f"[yellow]No entries found for '{keyword}' in {metadata_type}[/yellow]")
        return None

    if not silent:
        console.print(f"[green]Found {len(matches)} matches for '{keyword}' in {metadata_type}[/green]")

        # Display preview table
        preview_cols = matches.columns[:5].tolist()
        table = Table(show_header=True, header_style="bold magenta")
        for c in preview_cols:
            table.add_column(c, overflow="fold", justify="center")
        for _, row in matches.head(10).iterrows():
            table.add_row(*[str(row.get(c, "N/A")) for c in preview_cols])
        console.print(table)

    # --- Save full dataset ---
    results_dir = os.path.expanduser("~/Chip_Atlasmcp/results")
    os.makedirs(results_dir, exist_ok=True)
    fname = f"chip_atlas_{keyword}_{metadata_type}.csv"
    fpath = os.path.join(results_dir, fname)
    matches.to_csv(fpath, index=False)
    if not silent:
        console.print(f"[green]Full dataset saved to:[/green] {fpath}\n")

    return matches


# -----------------------
# 5️⃣ Save helper
# -----------------------
def save_full_dataset(df, gene: str, metadata_type: str, silent: bool = False):
    """Save the complete filtered dataset (all rows and columns) as CSV."""
    try:
        if df is None or (hasattr(df, "empty") and df.empty):
            if not silent:
                console.print(f"[yellow]No data to save for {gene} ({metadata_type})[/yellow]")
            return

        results_dir = os.path.expanduser("~/Chip_Atlasmcp/results")
        os.makedirs(results_dir, exist_ok=True)
        filename = f"chip_atlas_{gene}_{metadata_type}.csv"
        filepath = os.path.join(results_dir, filename)
        df.to_csv(filepath, index=False, encoding="utf-8")
        if not silent:
            console.print(f"[green]Full dataset saved successfully:[/green] {filepath}")
    except Exception as e:
        if not silent:
            console.print(f"[red]Error while saving dataset:[/red] {e}")



# """
# chip_Atlasmcp.py
# Full extended module for retrieving and processing data from the ChIP-Atlas database.

# Features:
# - Supports all 5 metadata types (experiment, file, analysis, antigen, celltype)
# - Automatically downloads and extracts files if missing
# - Handles TSV or CSV formats automatically
# - Filters by user-provided keyword (gene, antigen, or cell type)
# - Displays top 25–50 entries neatly in console
# - Saves full results with all metadata fields as CSV
# """

# import os
# import zipfile
# import requests
# import pandas as pd
# from io import BytesIO
# from typing import List, Dict
# from rich.console import Console
# from rich.table import Table

# console = Console()

# # -----------------------
# # 1️⃣ Metadata URLs
# # -----------------------
# METADATA_SPECS = {
#     "experiment_list": {
#         "filename": "chip_atlas_experiment_list.zip",
#         "url": "https://dbarchive.biosciencedbc.jp/data/chip-atlas/LATEST/chip_atlas_experiment_list.zip",
#         "unzipped_files": ["chip_atlas_experiment_list.tsv", "chip_atlas_experiment_list.csv"],
#     },
#     "file_list": {
#         "filename": "chip_atlas_file_list.zip",
#         "url": "https://dbarchive.biosciencedbc.jp/data/chip-atlas/LATEST/chip_atlas_file_list.zip",
#         "unzipped_files": ["chip_atlas_file_list.tsv", "chip_atlas_file_list.csv"],
#     },
#     "analysis_list": {
#         "filename": "chip_atlas_analysis_list.zip",
#         "url": "https://dbarchive.biosciencedbc.jp/data/chip-atlas/LATEST/chip_atlas_analysis_list.zip",
#         "unzipped_files": ["chip_atlas_analysis_list.tsv", "chip_atlas_analysis_list.csv"],
#     },
#     "antigen_list": {
#         "filename": "chip_atlas_antigen_list.zip",
#         "url": "https://dbarchive.biosciencedbc.jp/data/chip-atlas/LATEST/chip_atlas_antigen_list.zip",
#         "unzipped_files": ["chip_atlas_antigen_list.tsv", "chip_atlas_antigen_list.csv"],
#     },
#     "celltype_list": {
#         "filename": "chip_atlas_celltype_list.zip",
#         "url": "https://dbarchive.biosciencedbc.jp/data/chip-atlas/LATEST/chip_atlas_celltype_list.zip",
#         "unzipped_files": ["chip_atlas_celltype_list.tsv", "chip_atlas_celltype_list.csv"],
#     },
# }


# # -----------------------
# # 2️⃣ Ensure file exists or download
# # -----------------------
# def ensure_metadata_file(metadata_type: str) -> str:
#     """Ensure the metadata file exists locally, download if missing."""
#     if metadata_type not in METADATA_SPECS:
#         console.print(f"[red]Unknown metadata type: {metadata_type}[/red]")
#         return None

#     spec = METADATA_SPECS[metadata_type]
#     base_dir = os.path.expanduser("~/Chip_Atlasmcp")
#     os.makedirs(base_dir, exist_ok=True)

#     # Check if file already present
#     for fname in spec["unzipped_files"]:
#         fpath = os.path.join(base_dir, fname)
#         if os.path.exists(fpath):
#             console.print(f"[green]Found local file for {metadata_type}:[/green] {fpath}")
#             return fpath

#     # Download otherwise
#     console.print(f"[yellow]Downloading {metadata_type} from {spec['url']}...[/yellow]")
#     try:
#         r = requests.get(spec["url"], timeout=60)
#         r.raise_for_status()
#         with zipfile.ZipFile(BytesIO(r.content)) as zf:
#             zf.extractall(base_dir)
#         console.print(f"[green]Extracted {metadata_type} into:[/green] {base_dir}")
#     except Exception as e:
#         console.print(f"[red]Error downloading/extracting {metadata_type}:[/red] {e}")
#         return None

#     # Verify extracted file exists
#     for fname in spec["unzipped_files"]:
#         fpath = os.path.join(base_dir, fname)
#         if os.path.exists(fpath):
#             return fpath

#     console.print(f"[red]Error: could not locate {metadata_type} file after extraction.[/red]")
#     return None


# # -----------------------
# # 3️⃣ Load metadata safely
# # -----------------------
# def load_metadata(metadata_type: str) -> pd.DataFrame:
#     """Load a metadata table into a pandas DataFrame."""
#     fpath = ensure_metadata_file(metadata_type)
#     if not fpath:
#         return None

#     try:
#         sep = "\t" if fpath.endswith(".tsv") else None
#         df = pd.read_csv(fpath, sep=sep, dtype=str, encoding="utf-8", engine="python")
#         if df.shape[1] == 1:
#             df = pd.read_csv(fpath, sep=",", dtype=str, encoding="utf-8", engine="python")
#     except UnicodeDecodeError:
#         df = pd.read_csv(fpath, sep=sep, dtype=str, encoding="latin1", engine="python")
#         if df.shape[1] == 1:
#             df = pd.read_csv(fpath, sep=",", dtype=str, encoding="latin1", engine="python")
#     except Exception as e:
#         console.print(f"[red]Error loading {metadata_type} file:[/red] {e}")
#         return None

#     df.columns = [c.strip() for c in df.columns]
#     console.print(f"[cyan]Loaded columns:[/cyan] {list(df.columns)}")
#     return df


# # -----------------------
# # 4️⃣ Fetch, filter, display, save
# # -----------------------
# def fetch_and_display(metadata_type: str, keyword: str, column_hint: str = "Antigen"):
#     """Fetch and display entries from the chosen metadata list filtered by keyword."""
#     df = load_metadata(metadata_type)
#     if df is None:
#         return

#     # --- Smart column detection ---
#     col = None
#     for c in df.columns:
#         if c.strip().lower() == "antigen":
#             col = c
#             break
#     if not col:
#         possible_cols = [c for c in df.columns if "antigen" in c.lower()]
#         if possible_cols:
#             col = sorted(possible_cols, key=len)[0]

#     if not col and "Cell type" in df.columns:
#         col = "Cell type"

#     if not col:
#         console.print(f"[red]No suitable column found in {metadata_type}[/red]")
#         return

#     console.print(f"[green]Using column:[/green] {col}")

#     # --- Search keyword (case-insensitive) ---
#     matches = df[df[col].astype(str).str.contains(keyword, case=False, na=False)]
#     if matches.empty:
#         console.print(f"[yellow]No entries found for '{keyword}' in {metadata_type}[/yellow]")
#         return

#     n = len(matches)
#     console.print(f"[green]Found {n} matches for '{keyword}' in {metadata_type}[/green]")

#     limit = min(50, max(25, n))
#     top = matches.head(limit)

#     # --- Custom display for analysis_list ---
#     if metadata_type == "analysis_list":
#         display_cols = [
#             "Antigen",
#             "Cell type class in Colocalization",
#             "Recorded (+) or not (-) in Target Genes",
#             "Genome assembly",
#         ]
#         display_cols = [c for c in display_cols if c in top.columns]
#         if not display_cols:
#             display_cols = top.columns[:4].tolist()

#         table = Table(show_header=True, header_style="bold magenta")
#         for c in display_cols:
#             table.add_column(c, overflow="fold", justify="center")

#         for _, row in top.iterrows():
#             table.add_row(*[str(row.get(c, "N/A")) for c in display_cols])

#         console.print(f"\n[bold cyan]Analysis List Results:[/bold cyan]")
#         console.print(table)

#     else:
#         # --- Generic display (other metadata types) ---
#         essential_cols = ["Experimental ID", "Antigen", "Cell type", "Genome assembly", "Title"]
#         available_cols = [c for c in essential_cols if c in top.columns]

#         table = Table(show_header=True, header_style="bold magenta")
#         for c in available_cols:
#             table.add_column(c, overflow="fold", justify="center")

#         for _, row in top.iterrows():
#             table.add_row(*[str(row.get(c, "N/A")) for c in available_cols])

#         console.print(f"\n[bold cyan]{metadata_type.replace('_', ' ').title()} Results:[/bold cyan]")
#         console.print(table)

#     # --- Save full dataset ---
#     results_dir = os.path.expanduser("~/Chip_Atlasmcp/results")
#     os.makedirs(results_dir, exist_ok=True)
#     fname = f"chip_atlas_{keyword}_{metadata_type}.csv"
#     fpath = os.path.join(results_dir, fname)
#     matches.to_csv(fpath, index=False)
#     console.print(f"[green]Full dataset saved to:[/green] {fpath}\n")

#     return matches


# # -----------------------
# # 5️⃣ Save helper
# # -----------------------
# def save_full_dataset(df, gene: str, metadata_type: str):
#     """Save the complete filtered dataset (all rows and columns) as CSV."""
#     try:
#         if df is None or (hasattr(df, "empty") and df.empty):
#             console.print(f"[yellow]No data to save for {gene} ({metadata_type})[/yellow]")
#             return

#         results_dir = os.path.expanduser("~/Chip_Atlasmcp/results")
#         os.makedirs(results_dir, exist_ok=True)
#         filename = f"chip_atlas_{gene}_{metadata_type}.csv"
#         filepath = os.path.join(results_dir, filename)
#         df.to_csv(filepath, index=False, encoding="utf-8")
#         console.print(f"[green]Full dataset saved successfully:[/green] {filepath}")
#     except Exception as e:
#         console.print(f"[red]Error while saving dataset:[/red] {e}")








