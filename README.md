# Superstore Business Analytics

An end-to-end exploratory analysis of Superstore retail orders. The project cleans the source workbook, engineers operational and profitability features, exports a reusable dataset, and presents decision-ready charts and KPIs.

## Highlights

| Metric | Result |
| --- | ---: |
| Cleaned order records | 9,994 |
| Total sales | $1,401,969.37 |
| Total profit | $160,583.73 |
| Overall profit margin | 11.45% |
| Unique orders | 5,009 |
| Average shipping duration | 3.96 days |

> The figures above are calculated from the included processed dataset. The source data and the original analysis logic are preserved.

## Project layout

```text
Superstore-Business-Analytics/
├── data/
│   ├── raw/sample_superstore_2019.xls       # Original Orders workbook
│   └── processed/cleaned_superstore_data.csv # Cleaned and engineered export
├── notebooks/superstore_business_analysis.ipynb # Main exploratory notebook
├── outputs/figures/                         # Generated charts
├── docs/
│   ├── data_dictionary.md
│   └── methodology.md
├── src/run_analysis.py                      # Reproducible analysis runner
├── requirements.txt
└── .gitignore
```

## Quick start

```bash
python -m venv .venv
```

Activate the environment, then install the dependencies:

```bash
pip install -r requirements.txt
jupyter notebook notebooks/superstore_business_analysis.ipynb
```

To regenerate the processed data and figures without opening Jupyter:

```bash
python src/run_analysis.py
```

The runner reads `data/raw/sample_superstore_2019.xls`, writes the processed CSV to `data/processed/`, and regenerates charts in `outputs/figures/`.

## Analysis scope

- Standardizes headers, removes duplicate records, fills missing postal codes, and caps sales/profit outliers with the IQR method.
- Adds shipping duration, profit margin, and sales-performance bands.
- Examines sales distribution, category and regional performance, product rankings, discount versus margin, shipping duration, and time trends.
- Reports executive KPIs for revenue, profit, margin, order volume, and delivery time.

## Notes

- The workbook is retained as supplied and is required to rerun the pipeline.
- `data/processed/cleaned_superstore_data.csv` and the existing figures are included so the results can be reviewed immediately.
- See `docs/methodology.md` for transformation details and `docs/data_dictionary.md` for field definitions.
