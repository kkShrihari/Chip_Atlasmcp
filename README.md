# 🧬 Chip_Atlasmcp  
**An MCP-powered Python tool for exploring ChIP-Atlas metadata.**  

This package allows researchers to query, filter, and save ChIP-Atlas datasets directly from the command line or through an MCP-compatible AI assistant (e.g., Anthropic Claude).  

It supports all **five metadata categories** from the [ChIP-Atlas database](https://chip-atlas.org):  
- `experiment_list`  
- `file_list`  
- `analysis_list`  
- `antigen_list`  
- `celltype_list`  

> 🔍 Example: You can instantly retrieve all ChIP-seq experiments or analyses related to a gene like **TP53**.

---

## 🧩 Features

✅ Fetch and parse large ChIP-Atlas metadata tables (TSV/CSV)  
✅ Automatic download and extraction of missing metadata files  
✅ Smart filtering by gene, antigen, or cell type  
✅ Rich table display in terminal  
✅ Full dataset export as CSV under `~/Chip_Atlasmcp/results/`  
✅ Integrated MCP server for AI-driven analysis (Claude / Uniport MCP)  

---

## ⚙️ Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/kkShrihari/Chip_Atlasmcp.git
cd Chip_Atlasmcp
2️⃣ (Optional but recommended) Create a virtual environment
bash
Copy code
python3 -m venv venv
source venv/bin/activate
3️⃣ Install dependencies
bash
Copy code
pip install -r requirements.txt
💻 CLI Usage
Run the CLI via Python:

bash
Copy code
python -m Chip_Atlasmcp fetch TP53 --metadata-type analysis_list
Example outputs:

sql
Copy code
Retrieving ChipAtlas analysis_list data for: TP53
Found local file for analysis_list: /home/user/Chip_Atlasmcp/chip_atlas_analysis_list.csv
Loaded columns: ['Antigen', 'Cell type class in Colocalization', ...]
Using column: Antigen
Found 4 matches for 'TP53' in analysis_list
✅ Full dataset saved to: ~/Chip_Atlasmcp/results/chip_atlas_TP53_analysis_list.csv
Supported metadata types:
Metadata Type	Description
experiment_list	ChIP-seq experiment summaries
file_list	Downloadable data files
analysis_list	Precomputed co-localization and target gene analyses
antigen_list	Antibody and target protein list
celltype_list	Cell-type ontology and classification

🧠 Example: Fetching other data
Fetch all cell-type information related to HCT116:

bash
Copy code
python -m Chip_Atlasmcp fetch HCT116 --metadata-type celltype_list
Fetch experiment data for H3K27ac:

bash
Copy code
python -m Chip_Atlasmcp fetch H3K27ac --metadata-type experiment_list
🤖 MCP Integration
This project includes a built-in MCP server (mcp_server.py), allowing tools like Claude Desktop MCP, Uniport, or OpenDevin to interact with ChIP-Atlas data.

Run the MCP Server
bash
Copy code
python Chip_Atlasmcp/mcp_server.py --serve
Example MCP Commands (in Claude)
less
Copy code
@mcp ping
→ pong: hello

@mcp fetch_chip_atlas TP53 --metadata-type analysis_list
→ Returns summary + preview of ChIP-Atlas results for TP53
⚠️ Note on Data Availability
Some metadata files (like antigen_list and celltype_list) may temporarily fail to download from the ChIP-Atlas archive because:

The source URLs occasionally return 503 Service Unavailable responses.

These are server-side issues from the ChIP-Atlas hosting service (dbarchive.biosciencedbc.jp).

Other metadata (such as experiment_list and analysis_list) remains fully accessible and functional.

✅ The module handles these gracefully — missing data won’t break your workflow.

📁 Output
All filtered datasets are saved automatically under:

bash
Copy code
~/Chip_Atlasmcp/results/
Example:

Copy code
chip_atlas_TP53_analysis_list.csv
chip_atlas_HCT116_celltype_list.csv
🧑‍💻 Author
Shrihari Kamalan Kumaraguruparan
📧 kkshrihari@gmail.com
🌐 GitHub Profile

📜 License
MIT License © 2025 Shrihari Kamalan Kumaraguruparan

You are free to use, modify, and distribute this project for academic or commercial purposes — just keep attribution intact.
