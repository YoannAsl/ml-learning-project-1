# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OpenClassrooms ML Intro Project 1: Global socio-economic and agricultural data analysis to identify country clusters for chicken export targeting. Uses PESTEL framework with 9+ datasets from FAO, World Bank, and WorldData sources.

**Goal**: Cross-sectional analysis of 2024 data to understand structural drivers of Cost of Living and Food Price Inflation, then cluster countries for market targeting.

## Commands

```bash
# Setup
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Run data cleaning pipeline (generates merged_data_cleaned.csv)
python clean_data_complete_2024.py

# Start Jupyter
jupyter notebook
```

## Project Workflow

1. **cleaning.ipynb** - Initial data loading, standardization of country names, handling missing values, merging raw CSVs into `merged_data_cleaned.csv`

2. **exploration.ipynb** - Time series validation, distribution plots, correlation matrices, heatmaps

3. **analysis.ipynb** - PCA (correlation circle, projection of individuals), HAC clustering, k-means clustering

## Architecture

### Data Pipeline (`clean_data_complete_2024.py`)

Modular processing functions that can be run standalone or imported:
- `load_country_codes()` - Loads ISO-alpha3 and M49 code mappings from `data/country_codes.csv`
- `process_*()` functions - Each handles one dataset with LOCF (Last Observation Carried Forward) for 2024 missing values
- `merge_datasets()` - Outer joins all datasets on `(Country Code, Year)`, adds region info
- `load_and_clean_data()` - Main entry point, orchestrates the full pipeline

### Key Data Columns

After merging, data is keyed by `(Country Code, Year)` with ISO-alpha3 codes. Main indicators:
- Cost index, Purchasing power index
- Food Price Inflation (Mean)
- GDP per capita (current US$)
- LPI Score (Logistics Performance Index)
- Political stability indicators (Control of Corruption, Political Stability, etc.)
- Import/Export quantities (chickens)
- Urban population (%), Unemployment (%), Share of Organic Agricultural land (%)

### Data Sources (`data/` directory)

Raw CSVs from FAO/World Bank. Country codes use M49 (FAO) or ISO-alpha3 depending on source. The pipeline normalizes all to ISO-alpha3.
