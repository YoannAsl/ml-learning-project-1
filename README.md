# Global Socio-Economic & Agricultural Analysis 2024

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Pandas](https://img.shields.io/badge/pandas-Data%20Analysis-150458)
![Status](https://img.shields.io/badge/Status-Active-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

A comprehensive data analysis project exploring the relationships between global economic indicators, agricultural metrics, and social factors. This project focuses on a cross-sectional analysis of 2024 data to understand the structural drivers behind Cost of Living and Food Price Inflation.

## 📖 Description

This project aggregates and analyzes diverse datasets—ranging from GDP and Political Stability to Logistics Performance and Organic Agriculture—to provide a snapshot of the global state in 2024. 

The primary goal is to move beyond simple time-series evolution and conduct a **Cross-Sectional Analysis** to answer key questions:
*   What drives differences in **Cost of Living** between countries?
*   How do infrastructure (**LPI**) and governance correlate with **Food Price Inflation**?
*   Can countries be clustered into distinct profiles based on their structural reality?

**Key Features:**
*   **Data Integration:** Merges 9+ distinct CSV datasets into a unified analytical structure.
*   **2024 Snapshot:** Focused analysis on the most recent data available to model current world dynamics.
*   **Correlation Analysis:** Identifies structural drivers (e.g., Corruption, Logistics) behind economic outcomes.
*   **Visualization:** Includes global heatmaps, distribution plots, and correlation matrices.

## 📂 Data Sources

The analysis relies on the following datasets located in the `data/` directory:

| Dataset | Description |
| :--- | :--- |
| `Cost of living - purchasing power index 2024.csv` | Key target variable for 2024 analysis. |
| `Food price inflation - FAO_CP_23014.csv` | Inflation metrics for food products. |
| `GDP per Capita in USD - GDP per capita.csv` | Economic baseline data. |
| `Political 2015-2023.csv` | Governance and stability indicators. |
| `LPI_2014_to_2023.csv` | Logistics Performance Index (Infrastructure). |
| `Unemployment 2015-2024.csv` | Labor market statistics. |
| `Share of Organic Agricultural land.csv` | Agricultural sustainability metrics. |
| `Chicken-Turkey Import-Export quant.csv` | Trade data specific to poultry. |
| `Urban population (% of total population).csv` | Demographic urbanization trends. |

## 🛠 Installation

### Prerequisites
*   Python 3.8 or higher
*   Jupyter Notebook or JupyterLab

### Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/project-name.git
    cd project-name
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Windows
    python -m venv .venv
    .venv\Scripts\activate

    # macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Quick Start / Usage

The project workflow is divided into two main stages: Data Cleaning and Visualization.

### 1. Data Cleaning
Run the `cleaning.ipynb` notebook first. This notebook:
*   Loads the raw CSV files from the `data/` folder.
*   Standardizes country names and handles missing values.
*   Merges all datasets into a master file: `merged_data_cleaned.csv`.

### 2. Analysis & Visualization
Run the `visualization.ipynb` notebook to generate insights. This notebook performs:
*   **Descriptive Analysis:** Mapping the "State of the World" in 2024.
*   **Correlation Heatmaps:** Visualizing relationships between variables (e.g., LPI vs. Inflation).
*   **Clustering:** Grouping countries based on economic and structural similarities.

**Example Code Snippet (Loading & Filtering):**
```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the cleaned dataset
df = pd.read_csv('merged_data_cleaned.csv')

# Focus on 2024 Snapshot
df_2024 = df[df['Year'] == 2024].copy()
df_2024.dropna(subset=['Country Name', 'Cost Index'], inplace=True)

# Visualize Correlation
plt.figure(figsize=(10, 8))
sns.heatmap(df_2024.corr(), annot=True, cmap='coolwarm')
plt.title('2024 Global Indicators Correlation')
plt.show()
```

## 📊 Methodology

The analysis follows a structured approach as detailed in `time_series_analysis_guide.md`:

1.  **Data Preparation:** Isolating 2024 data and engineering "Trend" features from historical data.
2.  **Descriptive Analysis:** Using histograms and maps to visualize variable distributions (e.g., "High Inflation Zones").
3.  **Correlation & Drivers:** Hypothesis testing using correlation matrices (e.g., "Does better logistics lower food inflation?").
4.  **Clustering:** K-Means clustering to define country profiles (e.g., "Wealthy & Stable" vs. "Crisis States").

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1.  Fork the project.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors & Acknowledgments

*   **Data Sources:** FAO, World Bank, and other open data repositories.
*   **Contributors:** [Your Name]

---
*For more details on the year selection strategy, please refer to `year_selection_analysis.md`.*
