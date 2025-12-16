import json
import os

NOTEBOOK_CONFIG = [
    {
        'filename': 'food_inflation_cleaning.ipynb',
        'action': 'rename',
        'source_col': 'REF_AREA'
    },
    {
        'filename': 'import_export_cleaning.ipynb',
        'action': 'map_m49',
        'source_col': 'Area Code (M49)'
    },
    {
        'filename': 'logistics_perf_cleaning.ipynb',
        'action': 'map_name',
        'source_col': 'Country'
    },
    {
        'filename': 'politics_cleaning.ipynb',
        'action': 'rename',
        'source_col': 'Country Code'
    },
    {
        'filename': 'organic_ag_land_cleaning.ipynb',
        'action': 'map_m49',
        'source_col': 'Area Code (M49)'
    },
    {
        'filename': 'unemployment_cleaning.ipynb',
        'action': 'rename',
        'source_col': 'Country Code'
    },
    {
        'filename': 'cost_of_living_cleaning.ipynb',
        'action': 'map_name',
        'source_col': 'Country/Region'
    },
    {
        'filename': 'gdp_cleaning.ipynb',
        'action': 'rename',
        'source_col': 'REF_AREA'
    },
    {
        'filename': 'urban_pop_cleaning.ipynb',
        'action': 'rename',
        'source_col': 'Country Code'
    }
]

def create_code_cell(source_lines):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source_lines
    }

def create_markdown_cell(source_lines):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source_lines
    }

def generate_normalization_code(config):
    lines = [
        "# --- Normalization: Add ISO-alpha3 column ---\n",
        "\n",
        "# 1. Load UNSD Methodology for mapping\n",
        "try:\n",
        "    unsd_df = pd.read_csv('data/UNSD — Methodology.csv', sep=';')\n",
        "except FileNotFoundError:\n",
        "    unsd_df = pd.read_csv('../data/UNSD — Methodology.csv', sep=';')\n",
        "\n",
        "# 2. Create mappings\n",
        "unsd_df['Country or Area'] = unsd_df['Country or Area'].astype(str).str.strip()\n",
        "name_to_iso3 = unsd_df.set_index('Country or Area')['ISO-alpha3 Code'].to_dict()\n",
        "\n",
        "m49_to_iso3 = {}\n",
        "for idx, row in unsd_df.iterrows():\n",
        "    try:\n",
        "        # Handle potential non-numeric or NaN M49 codes\n",
        "        m49_code = int(row['M49 Code'])\n",
        "        m49_to_iso3[m49_code] = row['ISO-alpha3 Code']\n",
        "    except (ValueError, TypeError):\n",
        "        continue\n",
        "\n",
        "# 3. Apply mapping\n",
        "print(\"Applying ISO-alpha3 normalization...\")\n"
    ]
    
    if config['action'] == 'rename':
        lines.append(f"if '{config['source_col']}' in df.columns:\n")
        lines.append(f"    df['iso_alpha3'] = df['{config['source_col']}']\n")
        lines.append("    print(\"  Column copied to 'iso_alpha3'.\")\n")
        lines.append("else:\n")
        lines.append(f"    print(\"  Warning: Source column '{config['source_col']}' not found.\")\n")

    elif config['action'] == 'map_m49':
        lines.append(f"if '{config['source_col']}' in df.columns:\n")
        lines.append("    def get_iso(val):\n")
        lines.append("        try:\n")
        lines.append("            return m49_to_iso3.get(int(val), None)\n")
        lines.append("        except:\n")
        lines.append("            return None\n")
        lines.append(f"    df['iso_alpha3'] = df['{config['source_col']}'].apply(get_iso)\n")
        lines.append("    print(\"  Mapped M49 codes to 'iso_alpha3'.\")\n")
        lines.append("else:\n")
        lines.append(f"    print(\"  Warning: Source column '{config['source_col']}' not found.\")\n")

    elif config['action'] == 'map_name':
        lines.append(f"if '{config['source_col']}' in df.columns:\n")
        lines.append(f"    df['iso_alpha3'] = df['{config['source_col']}'].astype(str).str.strip().map(name_to_iso3)\n")
        lines.append("    print(\"  Mapped country names to 'iso_alpha3'.\")\n")
        lines.append("else:\n")
        lines.append(f"    print(\"  Warning: Source column '{config['source_col']}' not found.\")\n")

    lines.append("\n")
    lines.append("# Check results\n")
    lines.append("missing_iso = df['iso_alpha3'].isna().sum()\n")
    lines.append("if missing_iso > 0:\n")
    lines.append("    print(f\"  Warning: {missing_iso} rows have missing ISO-alpha3 codes.\")\n")
    lines.append("    print(df[df['iso_alpha3'].isna()][['" + config['source_col'] + "']].head())\n")
    
    return lines

def process_notebook(config):
    filepath = config['filename']
    if not os.path.exists(filepath):
        print(f"Skipping {filepath}: File not found")
        return

    print(f"Processing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    # Find insertion point: after the cell containing "df = pd.read_csv"
    insert_idx = -1
    for idx, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'code':
            source_text = "".join(cell['source'])
            if "df = pd.read_csv" in source_text and config['filename'] not in source_text: # avoid matching self if run multiple times (though simple check) 
                 # Check if we already inserted it
                is_already_inserted = False
                if idx + 1 < len(nb['cells']):
                    next_cell = nb['cells'][idx+1]
                    if "UNSD — Methodology" in "".join(next_cell['source']):
                         is_already_inserted = True
                
                if not is_already_inserted:
                    insert_idx = idx + 1
                    break
                else:
                    print("  Normalization logic seems already present.")
                    return

    if insert_idx != -1:
        # Generate code
        norm_code = generate_normalization_code(config)
        new_cell = create_code_cell(norm_code)
        
        # Insert markdown title
        md_cell = create_markdown_cell(["### Normalization Step: Add ISO-alpha3 Code"])
        
        # Insert both
        nb['cells'].insert(insert_idx, new_cell)
        nb['cells'].insert(insert_idx, md_cell)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1) # using indent=1 to minimize diff noise usually
        
        print(f"  Inserted normalization cell at index {insert_idx}.")
    else:
        print("  Could not find suitable insertion point (df = pd.read_csv).")

def main():
    for config in NOTEBOOK_CONFIG:
        process_notebook(config)

if __name__ == "__main__":
    main()
