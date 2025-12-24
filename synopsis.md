Here is the translation of your briefing into English, maintaining the original formatting:

Your goal will be to propose an **analysis of country clusters** that we can **target** for exporting our chickens. We will then conduct a more in-depth market study.

### 1.

-   Use a **PESTEL** analysis to find ideas for new data to add (we want at least 8 variables);
-   Retrieve and use any _open data_ you wish from [the FAO website](https://www.fao.org/faostat/en/#home), [the World Bank](https://data.worldbank.org), or [WorldData](https://www.worlddata.info).

### 2. **Prepare** and **clean** the data:

-   If you use multiple data sources, combine them into a single file.
-   Ideally, the analysis should include at least 100 countries (covering at least 60% of the world population).

### 3. Then, **move on** to **data exploration** (in Python or R); you can start by:

-   Analyzing the various **time series** in your data to confirm that the cleaning is correct (line charts, histograms, etc.);
-   Analyzing the different correlations between variables (correlation matrix, heatmap, pairplot, etc.).

### 4. Analytical Part

Perform a **PCA** (Principal Component Analysis) with dimensionality reduction and a **clustering** analysis (in a separate notebook from the data exploration):

-   Analyze the **correlation circle** and the **projection of individuals**.
-   Group the countries using either your PCA data or the raw data.
-   Start with **Hierarchical Agglomerative Clustering (HAC)**, followed by **k-means**.
