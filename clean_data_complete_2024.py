import pandas as pd
import numpy as np
import os

def load_country_codes(path="data/country_codes.csv"):
    """Loads and returns country code mappings."""
    if not os.path.exists(path):
        # Fallback for notebook running in different dir
        if os.path.exists(f"../{path}"):
            path = f"../{path}"
        else:
            print(f"Warning: {path} not found.")
            return None, {}, {}

    unsd_df = pd.read_csv(path, sep=",")
    unsd_df["Country"] = unsd_df["Country"].astype(str).str.strip()
    name_to_iso3 = unsd_df.set_index("Country")["ISO-alpha3 Code"].to_dict()
    
    m49_to_iso3 = {}
    for idx, row in unsd_df.iterrows():
        try:
            m49_code = int(row["M49 Code"])
            m49_to_iso3[m49_code] = row["ISO-alpha3 Code"]
        except (ValueError, TypeError):
            continue
            
    return unsd_df, name_to_iso3, m49_to_iso3

def process_cost_of_living(name_to_iso3, file_path="data/Cost of living - purchasing power index 2024.csv"):
    print("  Processing Cost of Living...")
    df = pd.read_csv(file_path)
    df = df.drop(columns=["Rank", "Ø Monthly income (USD)"])
    df.rename(columns={"Country/Region": "Country Name"}, inplace=True)
    df["Country Name"] = df["Country Name"].str.replace("*", "", regex=False).str.strip()
    df["Year"] = 2024
    
    if "Country Name" in df.columns:
        df["Country Code"] = df["Country Name"].str.strip().map(name_to_iso3)
    return df

def process_food_inflation(file_path="data/Food price inflation - FAO_CP_23014.csv"):
    print("  Processing Food Inflation...")
    df = pd.read_csv(file_path)
    
    min_year = 2015
    condition_to_keep = df["TIME_PERIOD"].str[:4].astype(int) >= min_year
    df = df[condition_to_keep].reset_index(drop=True)
    
    condition_to_keep = ~df["REF_AREA_LABEL"].isin(["South Asia", "World", "North America"])
    df = df[condition_to_keep]
    
    uniques = df.nunique()
    cols_to_drop = uniques[uniques <= 1].index
    df = df.drop(columns=cols_to_drop)
    
    df.rename(columns={
        "OBS_VALUE": "Food price inflation index",
        "REF_AREA": "Country Code", 
        "REF_AREA_LABEL": "Country Name", 
        "TIME_PERIOD": "Year"
    }, inplace=True)
    
    df["Year_Int"] = df["Year"].astype(str).str[:4].astype(int)
    df_yearly = df.groupby(["Country Code", "Year_Int"])["Food price inflation index"].mean().reset_index()
    df_yearly.rename(columns={"Year_Int": "Year", "Food price inflation index": "Food Price Inflation (Mean)"}, inplace=True)
    df = df_yearly
    
    # LOCF
    existing_2024 = df[df["Year"] == 2024]["Country Code"].unique()
    rows_2023 = df[df["Year"] == 2023]
    missing_2024_mask = ~rows_2023["Country Code"].isin(existing_2024)
    rows_to_copy = rows_2023[missing_2024_mask].copy()
    if not rows_to_copy.empty:
        rows_to_copy["Year"] = 2024
        df = pd.concat([df, rows_to_copy], ignore_index=True)
        
    return df

def process_gdp(file_path="data/GDP per Capita in USD - GDP per capita.csv"):
    print("  Processing GDP per Capita...")
    df = pd.read_csv(file_path)
    uniques = df.nunique()
    cols_to_drop = uniques[uniques <= 1].index
    df = df.drop(columns=cols_to_drop)
    
    rows_to_keep_condition = df["TIME_PERIOD"] >= 2015
    df = df[rows_to_keep_condition].reset_index(drop=True)
    
    df.rename(columns={
        "REF_AREA": "Country Code", 
        "REF_AREA_LABEL": "Country Name", 
        "TIME_PERIOD": "Year", 
        "OBS_VALUE": "GDP per capita (current US$)"
    }, inplace=True)

    # LOCF
    existing_2024 = df[df["Year"] == 2024]["Country Code"].unique()
    rows_2023 = df[df["Year"] == 2023]
    missing_2024_mask = ~rows_2023["Country Code"].isin(existing_2024)
    rows_to_copy = rows_2023[missing_2024_mask].copy()
    if not rows_to_copy.empty:
        print(f"    LOCF: Adding {len(rows_to_copy)} missing 2024 records for GDP.")
        rows_to_copy["Year"] = 2024
        df = pd.concat([df, rows_to_copy], ignore_index=True)
        
    return df

def process_import_export(m49_to_iso3, file_path="data/Chicken-Turkey Import-Export quant.csv"):
    print("  Processing Chicken Import/Export...")
    df = pd.read_csv(file_path)
    uniques = df.nunique()
    cols_to_drop = uniques[uniques <= 1].index
    df = df.drop(columns=cols_to_drop)
    df = df.drop(columns=["Element Code", "Item Code (CPC)", "Year Code", "Flag", "Flag Description"], errors='ignore')
    
    df = df[df["Item"] == "Chickens"].reset_index(drop=True)
    df = df.drop(columns=["Item"])
    df.rename(columns={"Area": "Country Name"}, inplace=True)
    
    # LOCF
    rows_to_copy = df[df["Year"] == 2023].copy()
    rows_to_copy["Year"] = 2024
    df = pd.concat([df, rows_to_copy], ignore_index=True)
    
    # Normalize
    def get_iso(val):
        try:
            return m49_to_iso3.get(int(val), None)
        except:
            return None

    if "Area Code (M49)" in df.columns:
        df["Country Code"] = df["Area Code (M49)"].apply(get_iso)

    df = df.pivot_table(
        index=["Country Code", "Year"], columns="Element", values="Value", aggfunc="first"
    ).reset_index()
    df.columns.name = None
    df = df.rename(columns={"Import quantity": "Import", "Export quantity": "Export"})
    
    return df

def process_lpi(name_to_iso3, file_path="data/LPI_2014_to_2023.csv"):
    print("  Processing LPI...")
    df = pd.read_csv(file_path)
    df.rename(columns={"Economy": "Country Name"}, inplace=True)
    
    # LOCF
    rows_to_copy = df[df["Year"] == 2023].copy()
    rows_to_copy["Year"] = 2024
    df = pd.concat([df, rows_to_copy], ignore_index=True)
    
    if "Country Name" in df.columns:
        df["Country Code"] = df["Country Name"].str.strip().map(name_to_iso3)
        
    return df

def process_organic_land(m49_to_iso3, file_path="data/Share of Organic Agricultural land.csv"):
    print("  Processing Organic Land...")
    df = pd.read_csv(file_path)
    df = df.drop(columns=["Element Code", "Item Code", "Year Code", "Flag", "Flag Description"], errors='ignore')
    df = df[df["Element"] == "Share in Agricultural land"].reset_index(drop=True)
    df.rename(columns={"Value": "Share of Organic Agricultural land (%)", "Area": "Country Name"}, inplace=True)
    
    uniques = df.nunique()
    cols_to_drop = uniques[uniques <= 1].index
    df = df.drop(columns=cols_to_drop)
    
    # LOCF
    rows_to_copy = df[df["Year"] == 2023].copy()
    rows_to_copy["Year"] = 2024
    df = pd.concat([df, rows_to_copy], ignore_index=True)
    
    # Normalize
    def get_iso(val):
        try:
            return m49_to_iso3.get(int(val), None)
        except:
            return None

    if "Area Code (M49)" in df.columns:
        df["Country Code"] = df["Area Code (M49)"].apply(get_iso)
        df.drop(columns=["Area Code (M49)"], inplace=True)
        
    return df

def process_politics(file_path="data/Political 2015-2023.csv"):
    print("  Processing Politics...")
    df = pd.read_csv(file_path)
    df = df.drop_duplicates()
    df = df.drop(columns=["Series Code"], errors='ignore')
    df = df.iloc[:-3] # Remove footer rows if present as per analysis
    
    id_vars = ["Country Name", "Country Code", "Series Name"]
    year_cols = [c for c in df.columns if "[" in c] 
    
    df = df.melt(id_vars=id_vars, value_vars=year_cols, var_name="Year", value_name="Value")
    df["Year"] = df["Year"].str[:4].astype(int)
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    
    df = df.pivot_table(
        index=["Country Name", "Country Code", "Year"], columns="Series Name", values="Value"
    ).reset_index()
    df.columns.name = None
    
    # LOCF
    rows_to_copy = df[df["Year"] == 2023].copy()
    rows_to_copy["Year"] = 2024
    df = pd.concat([df, rows_to_copy], ignore_index=True)
    
    return df

def process_unemployment(file_path="data/Unemployment 2015-2024.csv"):
    print("  Processing Unemployment...")
    df = pd.read_csv(file_path)
    uniques = df.nunique()
    cols_to_drop = uniques[uniques <= 1].index
    df = df.drop(columns=cols_to_drop)
    
    id_vars = ["Country Name", "Country Code"]
    value_vars = [col for col in df.columns if col not in id_vars]
    
    df = df.melt(id_vars=id_vars, value_vars=value_vars, var_name="Year", value_name="Unemployment (% of total labor force)")
    df["Year"] = df["Year"].astype(int)
    
    # LOCF
    df = df.sort_values(by=["Country Code", "Year"])
    
    # Vectorized LOCF logic using groupby and fillna (safer than loop if properly sorted)
    # However, to strictly follow the "copy 2023 to 2024 if missing" logic:
    
    df_2023 = df[df["Year"] == 2023].set_index("Country Code")["Unemployment (% of total labor force)"]
    mask_2024_nan = (df["Year"] == 2024) & (df["Unemployment (% of total labor force)"].isna())
    
    def fill_from_2023(row):
        cc = row["Country Code"]
        if cc in df_2023.index:
            return df_2023.loc[cc]
        return np.nan

    print(f"    LOCF: found {mask_2024_nan.sum()} missing 2024 unemployment records.")
    locf_values = df.loc[mask_2024_nan].apply(fill_from_2023, axis=1)
    df.loc[mask_2024_nan, "Unemployment (% of total labor force)"] = locf_values
    
    return df

def process_urban_population(file_path="data/Urban population (% of total population).csv"):
    print("  Processing Urban Population...")
    df = pd.read_csv(file_path)
    uniques = df.nunique()
    cols_to_drop = uniques[uniques <= 1].index
    df = df.drop(columns=cols_to_drop)
    
    id_vars = ["Country Name", "Country Code"]
    value_vars = [col for col in df.columns if col not in id_vars]
    
    df = df.melt(id_vars=id_vars, value_vars=value_vars, var_name="Year", value_name="Urban population (% of total population)")
    df["Year"] = df["Year"].astype(int)
    
    # LOCF
    df = df.sort_values(by=["Country Code", "Year"])
    
    df_urban_2023 = df[df["Year"] == 2023].set_index("Country Code")["Urban population (% of total population)"]
    mask_urban_2024_nan = (df["Year"] == 2024) & (df["Urban population (% of total population)"].isna())
    
    def fill_urban_from_2023(row):
        cc = row["Country Code"]
        if cc in df_urban_2023.index:
            return df_urban_2023.loc[cc]
        return np.nan
        
    print(f"    LOCF: found {mask_urban_2024_nan.sum()} missing 2024 urban population records.")
    locf_urban_values = df.loc[mask_urban_2024_nan].apply(fill_urban_from_2023, axis=1)
    df.loc[mask_urban_2024_nan, "Urban population (% of total population)"] = locf_urban_values
    
    return df

def merge_datasets(dfs, unsd_df, region_path="data/region_codes.csv"):
    print("Merging all datasets...")
    final_df = dfs[0].copy()

    for i, df_next in enumerate(dfs[1:], 1):
        df_next = df_next.copy()
        
        if "Year" in final_df.columns:
            final_df.loc[:, "Year"] = final_df["Year"].astype(int)
        if "Year" in df_next.columns:
            df_next.loc[:, "Year"] = df_next["Year"].astype(int)
            
        final_df = final_df.dropna(subset=["Country Code"])
        df_next = df_next.dropna(subset=["Country Code"])
        
        cols_to_use = ["Country Code", "Year"] + [c for c in df_next.columns if c not in ["Country Code", "Year", "Country Name", "Country", "Country/Region"]]
        
        final_df = pd.merge(final_df, df_next[cols_to_use], on=["Country Code", "Year"], how="outer")

    final_df = final_df.sort_values(by=["Country Code", "Year"])
    
    # Add Country Name mapping finally
    iso3_to_name = unsd_df.set_index("ISO-alpha3 Code")["Country"].to_dict()
    final_df["Country Name"] = final_df["Country Code"].map(iso3_to_name)

    # Reorder
    cols = ["Country Name", "Country Code", "Year"] + [c for c in final_df.columns if c not in ["Country Name", "Country Code", "Year"]]
    final_df = final_df[cols]

    # Region info
    if not os.path.exists(region_path):
        if os.path.exists(f"../{region_path}"):
             region_path = f"../{region_path}"
             
    if os.path.exists(region_path):
        df_region = pd.read_csv(region_path)
        region_cols = ["alpha-3", "region", "sub-region"]
        df_region_clean = df_region[region_cols].copy()
        df_region_clean.rename(columns={"alpha-3": "Country Code", "region": "Region", "sub-region": "Sub-region"}, inplace=True)
        df_region_clean = df_region_clean.drop_duplicates(subset=["Country Code"])
        
        final_df = pd.merge(final_df, df_region_clean, on="Country Code", how="left")
        
        # reorder region
        cols = final_df.columns.tolist()
        if "Region" in cols:
            idx = cols.index("Country Code")
            cols.pop(cols.index("Region"))
            cols.insert(idx + 1, "Region")
            cols.pop(cols.index("Sub-region"))
            cols.insert(idx + 2, "Sub-region")
            final_df = final_df[cols]
    else:
        print("Warning: region_codes.csv not found.")
        
    return final_df

def load_and_clean_data(save_path="merged_data_cleaned.csv", verbose=True):
    if verbose:
        print("Loading and cleaning data...")
        
    unsd_df, name_to_iso3, m49_to_iso3 = load_country_codes()
    if unsd_df is None:
        return None

    cost_of_living_df = process_cost_of_living(name_to_iso3)
    food_inflation_df = process_food_inflation()
    gdp_df = process_gdp()
    import_export_df = process_import_export(m49_to_iso3)
    lpi_df = process_lpi(name_to_iso3)
    land_df = process_organic_land(m49_to_iso3)
    politics_df = process_politics()
    unemployment_df = process_unemployment()
    urban_pop_df = process_urban_population()

    dfs_to_merge = [
        gdp_df[["Country Code", "Year", "GDP per capita (current US$)"]],
        food_inflation_df,
        import_export_df,
        cost_of_living_df[["Country Code", "Year", "Cost index", "Purchasing power index"]],
        lpi_df[["Country Code", "Year", "LPI Score"]],
        politics_df,
        land_df[["Country Code", "Year", "Share of Organic Agricultural land (%)"]],
        unemployment_df[["Country Code", "Year", "Unemployment (% of total labor force)"]],
        urban_pop_df[["Country Code", "Year", "Urban population (% of total population)"]],
    ]
    
    final_df = merge_datasets(dfs_to_merge, unsd_df)

    if verbose:
        print(f"Merged data shape: {final_df.shape}")

    if save_path:
        if verbose:
            print(f"Saving merged data to {save_path}...")
        final_df.to_csv(save_path, index=False)
        if verbose:
            print("Done!")
            
    return final_df

if __name__ == "__main__":
    load_and_clean_data()
