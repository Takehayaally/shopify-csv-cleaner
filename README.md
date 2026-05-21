# Shopify CSV Cleaner

Validate and clean Shopify product CSV files before import. This MVP trims whitespace, normalizes prices, flags required-field gaps, and detects duplicate SKUs.

By TinyOps Tools. Support: q749381667@gmail.com.

## Usage

```powershell
python products/shopify-csv-cleaner/shopify_csv_cleaner.py --input products/shopify-csv-cleaner/examples/products.csv --cleaned-out products/shopify-csv-cleaner/examples/products.cleaned.csv --report-out products/shopify-csv-cleaner/examples/report.md
```

The script writes a cleaned CSV even when warnings are present.

## Paid Bundle

Launch price: $19 on Gumroad. The paid bundle is planned to include bulk examples, import checklist, and a commercial-use license.
