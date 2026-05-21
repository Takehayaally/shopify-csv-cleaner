from __future__ import annotations

import argparse
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path


REQUIRED_COLUMNS = ("Handle", "Title")
PRICE_COLUMNS = ("Variant Price", "Variant Compare At Price")


def clean_value(value: str | None) -> str:
    return " ".join(str(value or "").strip().split())


def clean_price(value: str) -> tuple[str, str | None]:
    cleaned = value.replace("$", "").replace(",", "").strip()
    if not cleaned:
        return "", None
    try:
        return f"{Decimal(cleaned):.2f}", None
    except InvalidOperation:
        return value, f"Invalid price: {value}"


def read_csv(path: Path) -> tuple[list[dict], list[str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV file has no header row.")
        return list(reader), list(reader.fieldnames)


def clean_rows(rows: list[dict], fieldnames: list[str]) -> tuple[list[dict], list[str]]:
    warnings: list[str] = []
    cleaned_rows: list[dict] = []
    seen_skus: dict[str, int] = {}

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
    for column in missing_columns:
        warnings.append(f"Missing required column: {column}")

    for index, row in enumerate(rows, start=2):
        cleaned = {field: clean_value(row.get(field, "")) for field in fieldnames}
        for column in REQUIRED_COLUMNS:
            if column in fieldnames and not cleaned.get(column):
                warnings.append(f"Row {index}: required field {column} is blank")

        for column in PRICE_COLUMNS:
            if column in fieldnames:
                cleaned[column], warning = clean_price(cleaned[column])
                if warning:
                    warnings.append(f"Row {index}: {warning}")

        sku = cleaned.get("Variant SKU", "")
        if sku:
            if sku in seen_skus:
                warnings.append(f"Row {index}: duplicate Variant SKU {sku} also appears on row {seen_skus[sku]}")
            else:
                seen_skus[sku] = index
        cleaned_rows.append(cleaned)

    return cleaned_rows, warnings


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_report(path: Path, input_path: Path, rows: list[dict], warnings: list[str]) -> None:
    lines = [
        "# Shopify CSV Cleaner Report",
        "",
        f"- Input: `{input_path}`",
        f"- Rows checked: {len(rows)}",
        f"- Warnings: {len(warnings)}",
        "",
        "## Warnings",
        "",
    ]
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- None")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Clean and validate Shopify product CSV files.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--cleaned-out", default="products.cleaned.csv")
    parser.add_argument("--report-out", default="shopify-csv-report.md")
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    rows, fieldnames = read_csv(input_path)
    cleaned_rows, warnings = clean_rows(rows, fieldnames)
    write_csv(Path(args.cleaned_out), cleaned_rows, fieldnames)
    write_report(Path(args.report_out), input_path, cleaned_rows, warnings)
    print(f"Cleaned {len(cleaned_rows)} rows with {len(warnings)} warnings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
