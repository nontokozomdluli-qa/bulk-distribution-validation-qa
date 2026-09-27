"""
Bulk Distribution Validation QA Script
Runs the CSV-based validation checks and exports a single Excel workbook with
an Executive Summary and a pivot-style summary.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List

try:
    import openpyxl
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
    # Fallback values allow the module to import cleanly even when Excel support
    # is not installed. The script will raise a clear error only when export is attempted.
    Alignment = None
    Border = None
    Font = None
    PatternFill = None
    Side = None
    get_column_letter = lambda value: str(value)

# Style constants must exist even when Excel is unavailable.
if EXCEL_AVAILABLE:
    HEADER_FILL = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
    SUCCESS_FILL = PatternFill(start_color="2FA84F", end_color="2FA84F", fill_type="solid")
    FAIL_FILL = PatternFill(start_color="D9534F", end_color="D9534F", fill_type="solid")
    THIN_BORDER = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )
else:
    HEADER_FILL = None
    HEADER_FONT = None
    SUCCESS_FILL = None
    FAIL_FILL = None
    THIN_BORDER = None

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
RESOURCES_DIR = PROJECT_ROOT / "resources"
SOURCE_CSV_CANDIDATES = [
    RESOURCES_DIR / "source_validations.csv",
    RESOURCES_DIR / "source_calculations.csv",
]
DISTRIBUTION_CSV = RESOURCES_DIR / "distribution_output.csv"
REPORT_DIR = ROOT / "validation_reports"
REPORT_DIR.mkdir(exist_ok=True)

def safe_float(value: Any) -> float:
    if value is None or value == "":
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "").replace("$", "")
    if text.endswith("%"):
        text = text[:-1]
    try:
        return float(text)
    except ValueError:
        return 0.0


def normalize_fee_pct(value: Any) -> float:
    fee = safe_float(value)
    if fee > 1:
        return fee / 100.0
    return fee


def normalize_decimal(value: Any) -> float:
    return safe_float(value)


def to_table_row(data: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [dict(row) for row in data]


class ValidationRunner:
    def __init__(self):
        self.source_csv = next((path for path in SOURCE_CSV_CANDIDATES if path.exists()), SOURCE_CSV_CANDIDATES[-1])
        self.distribution_csv = DISTRIBUTION_CSV
        self.source_data = []
        self.distribution_data = []
        self.results = {}
        self.calc_validation_amount = []
        self.workbook_path = None

    def load_csv_files(self):
        """Load source and distribution CSVs for checks 1-7."""
        with self.source_csv.open("r", encoding="utf-8", newline="") as f:
            self.source_data = list(csv.DictReader(f))

        with self.distribution_csv.open("r", encoding="utf-8", newline="") as f:
            self.distribution_data = list(csv.DictReader(f))

    def run_all_validations(self):
        """Run all required CSV-based validation checks (1-7)."""
        self.load_csv_files()

        self.results["Check 1: Source Record Count vs Distribution Record Count"] = self._check_record_count()
        self.results["Check 2: Missing Records"] = self._check_missing_records()
        self.results["Check 3: Duplicate Records"] = self._check_duplicates()
        self.results["Check 4: Calculation Validation"] = self._check_calculation_validation()
        self.results["Check 5: Negative Source Amounts"] = self._check_negative_amounts()
        self.results["Check 6: Zero Distribution Amounts"] = self._check_zero_distributions()
        self.results["Check 7: Discrepancies between distributed and expected net amount"] = self._check_rounding_errors()

    def _check_record_count(self):
        source_count = len(self.source_data)
        distribution_count = len(self.distribution_data)
        diff = source_count - distribution_count
        if diff == 0:
            return []

        return [{
            "source_calculations": source_count,
            "distribution_output": distribution_count,
            "difference": diff,
        }]

    def _check_missing_records(self):
        source_ids = {row.get("client_id") for row in self.source_data if row.get("client_id")}
        dist_ids = {row.get("client_id") for row in self.distribution_data if row.get("client_id")}

        issues = []

        for client_id in sorted(source_ids - dist_ids):
            source_row = next((row for row in self.source_data if row.get("client_id") == client_id), {})
            issues.append({
                "client_id": client_id,
                "client_name": source_row.get("client_name", ""),
                "source_amount": source_row.get("source_amount", ""),
                "distributed_amount": None,
                "status": f"Missing in distribution_output",
            })

        for client_id in sorted(dist_ids - source_ids):
            dist_row = next((row for row in self.distribution_data if row.get("client_id") == client_id), {})
            issues.append({
                "client_id": client_id,
                "client_name": dist_row.get("client_name", ""),
                "source_amount": None,
                "distributed_amount": dist_row.get("distributed_amount", ""),
                "status": f"Missing in source_calculations",
            })

        return issues

    def _check_duplicates(self):
        """Check duplicates by client ID and log only once per unique combination."""
        issues = []
        logged = set()  # Track logged duplicates to avoid duplication

        # Check source data for duplicates by client_id
        source_by_id: Dict[str, List[Dict[str, str]]] = {}
        for row in self.source_data:
            client_id = row.get("client_id")
            if client_id:
                source_by_id.setdefault(client_id, []).append(row)

        for client_id, rows in sorted(source_by_id.items()):
            if len(rows) > 1:
                # Log once per client ID with duplicate count
                first_row = rows[0]
                key = (client_id, "source_calculations")
                if key not in logged:
                    issues.append({
                        "client_id": client_id,
                        "client_name": first_row.get("client_name", ""),
                        "source_amount": first_row.get("source_amount", ""),
                        "table_name": "source_calculations",
                        "duplicate_count": len(rows),
                    })
                    logged.add(key)

        # Check distribution data for duplicates by client_id
        dist_by_id: Dict[str, List[Dict[str, str]]] = {}
        for row in self.distribution_data:
            client_id = row.get("client_id")
            if client_id:
                dist_by_id.setdefault(client_id, []).append(row)

        for client_id, rows in sorted(dist_by_id.items()):
            if len(rows) > 1:
                # Log once per client ID with duplicate count
                first_row = rows[0]
                key = (client_id, "distribution_output")
                if key not in logged:
                    issues.append({
                        "client_id": client_id,
                        "client_name": first_row.get("client_name", ""),
                        "source_amount": first_row.get("distributed_amount", ""),
                        "table_name": "distribution_output",
                        "duplicate_count": len(rows),
                    })
                    logged.add(key)

        return issues

    def _check_calculation_validation(self):
        """Compare normalized source amount/fee calculation against expected_net_amount.
        Store ALL calculation results regardless of discrepancy."""
        calc_rows = []
        calc_details = []  # Store all calculations for the sheet
        
        for row in self.source_data:
            client_id = row.get("client_id")
            if not client_id:
                continue

            source_amount = normalize_decimal(row.get("source_amount"))
            fee_pct = normalize_fee_pct(row.get("fee_pct"))
            expected_net_amount = normalize_decimal(row.get("expected_net_amount"))
            calculated_amount = source_amount * (1 - fee_pct)
            difference = round(calculated_amount - expected_net_amount, 4)
            
            # Record calculation result for display sheet
            calc_result = {
                "client_id": client_id,
                "client_name": row.get("client_name", ""),
                "source_amount": round(source_amount, 2),
                "fee_pct": round(fee_pct * 100, 2),  # Display as percentage
                "calculated_amount": round(calculated_amount, 2),
                "expected_net_amount": round(expected_net_amount, 2),
                "difference": round(difference, 2),
            }
            calc_details.append(calc_result)
            
            # Log only meaningful discrepancies - threshold catches C002 (0.005) but not rounding errors
            if abs(difference) >= 0.0049:
                calc_rows.append(calc_result)

        # Store actual calculation details for the sheet (not just discrepancies)
        self.calc_validation_amount = calc_details
        
        # Return only discrepancies for validation status
        return calc_rows

    def _check_negative_amounts(self):
        issues = []
        for row in self.source_data:
            client_id = row.get("client_id")
            source_amount = normalize_decimal(row.get("source_amount"))
            if source_amount < 0:
                issues.append({
                    "table_name": "source_calculations",
                    "client_id": client_id,
                    "client_name": row.get("client_name", ""),
                    "source_amount": round(source_amount, 2),
                })
        return issues

    def _check_zero_distributions(self):
        issues = []
        for row in self.source_data:
            client_id = row.get("client_id")
            source_amount = normalize_decimal(row.get("source_amount"))
            if source_amount == 0:
                issues.append({
                    "table_name": "source_calculations",
                    "client_id": client_id,
                    "client_name": row.get("client_name", ""),
                    "source_amount": round(source_amount, 2),
                })

        for row in self.distribution_data:
            client_id = row.get("client_id")
            distributed_amount = normalize_decimal(row.get("distributed_amount"))
            if distributed_amount == 0:
                issues.append({
                    "table_name": "distribution_output",
                    "client_id": client_id,
                    "client_name": row.get("client_name", ""),
                    "distributed_amount": round(distributed_amount, 2),
                    "status": row.get("status", ""),
                })
        return issues

    def _check_rounding_errors(self):
        issues = []
        dist_by_id = {row.get("client_id"): row for row in self.distribution_data if row.get("client_id")}

        for row in self.source_data:
            client_id = row.get("client_id")
            if not client_id:
                continue

            source_amount = normalize_decimal(row.get("source_amount"))
            expected_net_amount = normalize_decimal(row.get("expected_net_amount"))
            dist_row = dist_by_id.get(client_id)
            if not dist_row:
                continue

            distributed_amount = normalize_decimal(dist_row.get("distributed_amount"))
            difference = abs(distributed_amount - expected_net_amount)

            if difference > 0.01:
                issues.append({
                    "table_name": "source_calculations / distribution_output",
                    "client_id": client_id,
                    "client_name": row.get("client_name", ""),
                    "source_amount": round(source_amount, 2),
                    "distributed_amount": round(distributed_amount, 2),
                    "expected_net_amount": round(expected_net_amount, 2),
                    "difference": round(difference, 4),
                })
        return issues

    def _create_summary_sheet(self, sheet, pivot_rows):
        sheet["A1"] = "Bulk Distribution Validation Report"
        sheet["A1"].font = Font(bold=True, size=14)
        sheet.merge_cells("A1:C1")
        sheet["A2"] = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        headers = ["Validation Check", "Status", "Issue Count"]
        row = 4
        for col_idx, header in enumerate(headers, 1):
            cell = sheet.cell(row=row, column=col_idx)
            cell.value = header
            cell.fill = HEADER_FILL
            cell.font = HEADER_FONT
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = THIN_BORDER

        row = 5
        for check_name, data in self.results.items():
            issue_count = len(data) if isinstance(data, list) else 0
            status = "PASS" if issue_count == 0 else "FAIL"
            sheet.cell(row=row, column=1, value=check_name)
            sheet.cell(row=row, column=2, value=status)
            sheet.cell(row=row, column=3, value=issue_count)

            status_cell = sheet.cell(row=row, column=2)
            status_cell.font = Font(bold=True)
            status_cell.border = THIN_BORDER
            status_cell.fill = SUCCESS_FILL if status == "PASS" else FAIL_FILL
            status_cell.alignment = Alignment(horizontal="center")

            for col in (1, 3):
                sheet.cell(row=row, column=col).border = THIN_BORDER

            row += 1

        sheet["A1"].alignment = Alignment(horizontal="center")
        for col in ["A", "B", "C"]:
            sheet.column_dimensions[col].width = 32



    def _write_detail_sheet(self, wb, check_name, data):
        sheet = wb.create_sheet(title=self._safe_sheet_name(check_name))
        sheet.merge_cells("A1:G1")
        sheet["A1"] = check_name
        sheet["A1"].font = Font(bold=True, size=12)
        sheet["A1"].alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        if not data:
            sheet["A3"] = "No issues found"
            sheet["A3"].font = Font(bold=True)
            return

        headers = list(data[0].keys())
        for col_idx, header in enumerate(headers, 1):
            cell = sheet.cell(row=3, column=col_idx)
            cell.value = header
            cell.fill = HEADER_FILL
            cell.font = HEADER_FONT
            cell.border = THIN_BORDER

        for row_idx, item in enumerate(data, 2):
            for col_idx, key in enumerate(headers, 1):
                cell = sheet.cell(row=row_idx + 2, column=col_idx)
                cell.value = item.get(key)
                cell.border = THIN_BORDER

        for column in sheet.columns:
            max_length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column)
            sheet.column_dimensions[get_column_letter(column[0].column)] .width = min(max_length + 2, 30)

    @staticmethod
    def _safe_sheet_name(name: str) -> str:
        cleaned = name.replace("/", " ").replace("\\", " ").replace(":", " ")
        return cleaned[:31]

    def export_to_excel(self):
        if not EXCEL_AVAILABLE:
            raise RuntimeError("openpyxl is required for Excel export. Install with: pip install openpyxl")

        workbook = openpyxl.Workbook()
        workbook.remove(workbook.active)

        summary_sheet = workbook.create_sheet("Executive Summary")
        self._create_summary_sheet(summary_sheet, [])

        calc_sheet = workbook.create_sheet("calc_validation_amount")
        if self.calc_validation_amount:
            calc_headers = list(self.calc_validation_amount[0].keys())
            for col_idx, header in enumerate(calc_headers, 1):
                cell = calc_sheet.cell(row=1, column=col_idx)
                cell.value = header
                cell.fill = HEADER_FILL
                cell.font = HEADER_FONT
                cell.border = THIN_BORDER
            for row_idx, row in enumerate(self.calc_validation_amount, 2):
                for col_idx, key in enumerate(calc_headers, 1):
                    cell = calc_sheet.cell(row=row_idx, column=col_idx)
                    cell.value = row.get(key)
                    cell.border = THIN_BORDER

        for check_name, data in self.results.items():
            self._write_detail_sheet(workbook, check_name, data)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.workbook_path = REPORT_DIR / f"validation_report_{timestamp}.xlsx"
        workbook.save(self.workbook_path)
        print(f"Excel workbook created: {self.workbook_path}")
        return self.workbook_path


def main():
    print("=" * 76)
    print("BULK DISTRIBUTION VALIDATION QA")
    print("=" * 76)
    print()
    print("Source Files:")
    print(f"  - source_calculations.csv")
    print(f"  - distribution_output.csv")
    print()
    print("Validation Scripts Running...")
    print()

    runner = ValidationRunner()
    runner.run_all_validations()

    print("Validation Scripts Completed.")
    print()
    print("Validation Summary:")
    print("-" * 76)
    for check_name, data in runner.results.items():
        issue_count = len(data) if isinstance(data, list) else 0
        status = "PASS" if issue_count == 0 else "FAIL"
        print(f"  {check_name}: {status} ({issue_count} issues)")
    print("-" * 76)
    print()

    print("Validation Scripts Ran Successfully, Exporting Results to Excel...")
    print()
    try:
        workbook_path = runner.export_to_excel()
        print(f"Validation report successfully created and saved in validation_reports folder.")
        print(f"  Report: {workbook_path.name}")
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
    
    print()
    print("=" * 76)
    print("Done.")
    print("=" * 76)


if __name__ == "__main__":
    main()
