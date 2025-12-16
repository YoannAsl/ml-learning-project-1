import pandas as pd
import os

UNSD_PATH = 'data/UNSD — Methodology.csv'
DATA_DIR = 'data'

FILES_CONFIG = [
    {
        'filename': 'Food price inflation - FAO_CP_23014.csv',
        'action': 'rename',
        'source_col': 'REF_AREA'
    },
    {
        'filename': 'Chicken-Turkey Import-Export quant.csv',
        'action': 'map_m49',
        'source_col': 'Area Code (M49)'
    },
    {
        'filename': 'Logistics Performance Index 2023.csv',
        'action': 'map_name',
        'source_col': 'Country'
    },
    {
        'filename': 'Political 2015-2023.csv',
        'action': 'rename',
        'source_col': 'Country Code'
    },
    {
        'filename': 'Share of Organic Agricultural land.csv',
        'action': 'map_m49',
        'source_col': 'Area Code (M49)'
    },
    {
        'filename': 'Unemployment 2015-2024.csv',
        'action': 'rename',
        'source_col': 'Country Code'
    },
    {
        'filename': 'Cost of living - purchasing power index 2024.csv',
        'action': 'map_name',
        'source_col': 'Country/Region'
    },
    {
        'filename': 'GDP per Capita in USD - GDP per capita.csv',
        'action': 'rename',
        'source_col': 'REF_AREA'
    },
    {
        'filename': 'Urban population (% of total population).csv',
        'action': 'rename',
        'source_col': 'Country Code'
    }
]

def load_mappings():
    print(f"Loading mappings from {UNSD_PATH}...")
    unsd = pd.read_csv(UNSD_PATH, sep=';')
    
    # Create Name -> ISO3 map
    # Strip whitespace just in case
    unsd['Country or Area'] = unsd['Country or Area'].astype(str).str.strip()
    name_map = unsd.set_index('Country or Area')['ISO-alpha3 Code'].to_dict()
    
    # Create M49 -> ISO3 map
    # Convert M49 to integer to handle "004" vs "4"
    # Filter out non-numeric M49 if any (though usually they are numeric)
    m49_map = {}
    for index, row in unsd.iterrows():
        try:
            m49_int = int(row['M49 Code'])
            iso_code = row['ISO-alpha3 Code']
            m49_map[m49_int] = iso_code
        except (ValueError, TypeError):
            continue
            
    return name_map, m49_map

def process_file(config, name_map, m49_map):
    filepath = os.path.join(DATA_DIR, config['filename'])
    if not os.path.exists(filepath):
        print(f"Warning: File not found: {filepath}")
        return

    print(f"Processing {config['filename']}...")
    try:
        # Try reading with default separator first, usually comma
        # Some files might be different, but looking at previews most are comma.
        # UNSD was semicolon, but data files looked like commas in previews.
        df = pd.read_csv(filepath)
    except Exception:
        # Fallback for weird separators if needed
        df = pd.read_csv(filepath, sep=None, engine='python')

    # Check if target column already exists to avoid overwriting if run multiple times
    # But user might want to refresh. We will overwrite 'iso_alpha3'.
    
    new_col_name = 'iso_alpha3'
    
    if config['action'] == 'rename':
        source = config['source_col']
        if source in df.columns:
            # We copy instead of rename to preserve original data structure just in case,
            # but user asked to "have a column". Copy is safer.
            df[new_col_name] = df[source]
        else:
            print(f"  Error: Source column '{source}' not found.")
            return

    elif config['action'] == 'map_m49':
        source = config['source_col']
        if source in df.columns:
            # Convert source to int for mapping
            def get_iso_from_m49(val):
                try:
                    return m49_map.get(int(val), None)
                except (ValueError, TypeError):
                    return None
            
            df[new_col_name] = df[source].apply(get_iso_from_m49)
        else:
            print(f"  Error: Source column '{source}' not found.")
            return

    elif config['action'] == 'map_name':
        source = config['source_col']
        if source in df.columns:
            # Clean name for mapping
            df[new_col_name] = df[source].astype(str).str.strip().map(name_map)
            
            # Simple fuzzy fix for common mismatches if needed (optional)
            # e.g. "USA" -> "United States of America"
            # For now, we stick to direct map.
        else:
            print(f"  Error: Source column '{source}' not found.")
            return
            
    # Check for missing values
    missing = df[new_col_name].isna().sum()
    if missing > 0:
        print(f"  Warning: {missing} rows could not be mapped to ISO-alpha3.")
        # Optional: Print a few unmapped values to help debug
        unmapped = df[df[new_col_name].isna()]
        source_vals = unmapped[config['source_col']].unique()[:5]
        print(f"  Sample unmapped values: {source_vals}")

    df.to_csv(filepath, index=False)
    print(f"  Saved updated file to {filepath}")

def main():
    name_map, m49_map = load_mappings()
    
    for config in FILES_CONFIG:
        process_file(config, name_map, m49_map)

if __name__ == "__main__":
    main()
