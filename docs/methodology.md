# Methodology

## Data preparation

1. Load the `Orders` sheet from the supplied Excel workbook.
2. Standardize field names to lowercase snake_case.
3. Remove exact duplicate rows.
4. Fill missing postal codes with `5401`, consistent with the original notebook.
5. Cap `sales` and `profit` using the 1.5 × IQR rule rather than deleting rows.

## Derived features

- **Shipping duration:** ship date minus order date, in days.
- **Profit margin:** profit divided by sales, expressed as a percentage.
- **Sales performance:** Low, Medium, and High bands based on sales values of 50 and 200.

## Interpretation caveats

The IQR transformation changes extreme sales and profit values, so summary statistics in the processed dataset may differ from an unmodified source-data calculation. Profit margin is a line-level metric; overall margin should be calculated as total profit divided by total sales, not as the mean of line-level margins.
