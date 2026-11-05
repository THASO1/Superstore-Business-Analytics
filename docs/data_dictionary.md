# Data dictionary

The processed CSV retains the Superstore order fields and adds three analytical features.

| Field | Description |
| --- | --- |
| `row_id` | Source row identifier. |
| `order_id`, `order_date`, `ship_date` | Order identifier and transaction/shipping dates. |
| `ship_mode` | Delivery service level. |
| `customer_id`, `customer_name`, `segment` | Customer identifiers and market segment. |
| `country`, `city`, `state`, `postal_code`, `region` | Geographic attributes. |
| `product_id`, `category`, `sub_category`, `product_name` | Product hierarchy and product description. |
| `sales` | Order-line sales value after IQR capping. |
| `quantity` | Units sold. |
| `discount` | Discount rate applied to the line item. |
| `profit` | Order-line profit after IQR capping. |
| `shipping_duration` | Calendar days from order date to ship date. |
| `profit_margin` | `profit / sales × 100`. |
| `sales_performance` | Sales band: Low (≤50), Medium (50–200), or High (>200). |

The original workbook remains the system of record. The processed dataset is a reproducible analytical output, not a replacement for the source data.
