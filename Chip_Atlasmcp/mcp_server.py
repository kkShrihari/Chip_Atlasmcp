# === Inject local dependencies ===
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# === Silence console + print output when running as MCP ===
import builtins

if os.environ.get("MCP_SILENT", "1") == "1":
    # Disable normal print()
    builtins.print = lambda *a, **k: None
    try:
        from rich.console import Console
        import Chip_Atlasmcp
        silent_console = Console(file=open(os.devnull, "w"))
        Chip_Atlasmcp.console = silent_console
    except Exception:
        pass

# === Import MCP server ===
try:
    from mcp.server.fastmcp import FastMCPServer as FastMCP
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception as e:
        raise ImportError(f"Could not import FastMCP: {e}")

# === Import Chip Atlas Project ===
from Chip_Atlasmcp import Chip_Atlasmcp
from Chip_Atlasmcp import utils

# === Initialize MCP ===
mcp = FastMCP("Chip_Atlas MCP")

# -----------------------------
# 🔬 Fetch Chip Atlas Metadata
# -----------------------------
@mcp.tool()
async def fetch_chip_atlas(
    gene: str,
    metadata_type: str = "experiment_list"
):
    """
    Fetch ChIP-Atlas metadata and return structured JSON.

    Args:
        gene: Gene or antigen keyword (e.g. "TP53", "H3K4me3")
        metadata_type: experiment_list | file_list | analysis_list | antigen_list | celltype_list
    """
    try:
        loop = asyncio.get_event_loop()
        # Run with silent=True to suppress console output
        df = await loop.run_in_executor(None, Chip_Atlasmcp.fetch_and_display, metadata_type, gene, "Antigen", True)

        if df is None or getattr(df, "empty", True):
            return {
                "status": "no_data",
                "gene": gene,
                "metadata_type": metadata_type,
                "message": f"No results found for {gene} in {metadata_type}."
            }

        # Save dataset silently
        await loop.run_in_executor(None, Chip_Atlasmcp.save_full_dataset, df, gene, metadata_type, True)

        # Prepare preview for Claude
        preview = df.head(10).to_dict(orient="records")

        return {
            "status": "success",
            "gene": gene,
            "metadata_type": metadata_type,
            "rows_found": len(df),
            "columns": list(df.columns),
            "preview": preview
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

#  Version Info

@mcp.tool()
async def version_info():
    """Return version and author of Chip_Atlasmcp."""
    try:
        from Chip_Atlasmcp import __version__, __author__
        return {"version": __version__, "author": __author__}
    except Exception:
        return {"version": "0.1.0", "author": "Shrihari"}


#  Connectivity Test

@mcp.tool()
async def ping(msg: str = "hello"):
    """Ping test to confirm MCP connection."""
    return {"reply": f"pong: {msg}"}


#  Entry Point

if __name__ == "__main__":
    if "--serve" in sys.argv:
        asyncio.run(mcp.run())

