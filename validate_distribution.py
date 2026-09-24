from __future__ import annotations

import csv
import sqlite3
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "bulk_distribution_validation.db"
SOURCE_CSV = ROOT / "resources" / "source_calculations.csv"
DISTRIBUTION_CSV = ROOT / "resources" / "distribution_output.csv"


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    value = value.strip()
    if value == "" or value.lower() in {"null", "none"}:
        return None
    return float(value)


def load_csv_into_table(conn: sqlite3.Connection, table_name: str, csv_path: Path) -> None:
    with csv_path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    if not rows:
        return

    fieldnames = reader.fieldnames or []
    placeholders = ", ".join("?" for _ in fieldnames)
    columns = ", ".join(fieldnames)
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    values: list[tuple] = []
    for row in rows:
        value_tuple = []
        for field in fieldnames:
            raw = row.get(field)
            if field in {"source_amount", "fee_pct", "expected_net_amount", "distributed_amount"}:
                value_tuple.append(parse_float(raw))
            else:
                value_tuple.append(raw.strip() if raw is not None else None)
        values.append(tuple(value_tuple))

    conn.executemany(sql, values)
    conn.commit()


def bootstrap_database(conn: sqlite3.Connection) -> None:
    conn.execute("DROP TABLE IF EXISTS source_calculations")
    conn.execute("DROP TABLE IF EXISTS distribution_output")

    conn.execute(
        """
        CREATE TABLE source_calculations (
            client_id TEXT,
            client_name TEXT,
            source_amount REAL,
            fee_pct REAL,
            expected_net_amount REAL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE distribution_output (
            client_id TEXT,
            client_name TEXT,
            distributed_amount REAL,
            status TEXT
        )
        """
    )

    load_csv_into_table(conn, "source_calculations", SOURCE_CSV)
    load_csv_into_table(conn, "distribution_output", DISTRIBUTION_CSV)


def run_validation_queries(conn: sqlite3.Connection) -> list[tuple]:
    queries = [
        """
        SELECT
            src.record_count AS source_record_count,
            dist.record_count AS distribution_record_count,
            src.record_count - dist.record_count AS record_count_difference
        FROM (
            SELECT COUNT(*) AS record_count FROM source_calculations
        ) src
        CROSS JOIN (
            SELECT COUNT(*) AS record_count FROM distribution_output
        ) dist
        WHERE src.record_count <> dist.record_count
        """,
        """
        SELECT
            s.client_id,
            s.client_name,
            s.source_amount,
            'MISSING_IN_DISTRIBUTION' AS validation_issue
        FROM source_calculations s
        LEFT JOIN distribution_output d
            ON s.client_id = d.client_id
        WHERE d.client_id IS NULL

        UNION ALL

        SELECT
            d.client_id,
            d.client_name,
            NULL AS source_amount,
            'MISSING_IN_SOURCE' AS validation_issue
        FROM distribution_output d
        LEFT JOIN source_calculations s
            ON d.client_id = s.client_id
        WHERE s.client_id IS NULL
        """,
        """
        SELECT
            'source_calculations' AS table_name,
            client_id,
            client_name,
            source_amount,
            COUNT(*) AS duplicate_count
        FROM source_calculations
        GROUP BY client_id, client_name, source_amount
        HAVING COUNT(*) > 1
        """,
        """
        SELECT
            'distribution_output' AS table_name,
            client_id,
            client_name,
            distributed_amount AS source_amount,
            COUNT(*) AS duplicate_count
        FROM distribution_output
        GROUP BY client_id, client_name, distributed_amount
        HAVING COUNT(*) > 1
        """,
        """
        SELECT
            'source_calculations' AS table_name,
            client_id,
            MIN(client_name) AS client_name,
            MIN(source_amount) AS source_amount,
            COUNT(*) AS duplicate_count
        FROM source_calculations
        GROUP BY client_id
        HAVING COUNT(*) > 1
        """,
        """
        SELECT
            'distribution_output' AS table_name,
            client_id,
            MIN(client_name) AS client_name,
            MIN(distributed_amount) AS source_amount,
            COUNT(*) AS duplicate_count
        FROM distribution_output
        GROUP BY client_id
        HAVING COUNT(*) > 1
        """,
        """
        SELECT
            s.client_id,
            s.source_amount,
            s.expected_net_amount,
            (s.source_amount - (s.source_amount * s.fee_pct / 100.0)) AS correct_net_amount
        FROM source_calculations s
        WHERE ABS(s.expected_net_amount - (s.source_amount - (s.source_amount * s.fee_pct / 100.0))) > 0.01
        """,
        """
        SELECT
            client_id,
            source_amount
        FROM source_calculations
        WHERE source_amount < 0
        """,
        """
        SELECT
            client_id,
            client_name,
            distributed_amount,
            status
        FROM distribution_output
        WHERE distributed_amount = 0
        """,
        """
        SELECT
            s.client_id,
            s.expected_net_amount,
            d.distributed_amount,
            d.distributed_amount - s.expected_net_amount AS difference
        FROM source_calculations s
        INNER JOIN distribution_output d
            ON s.client_id = d.client_id
        WHERE ABS(d.distributed_amount - s.expected_net_amount) > 0.01
        """,
    ]

    results: list[tuple] = []
    for index, query in enumerate(queries, start=1):
        rows = conn.execute(query).fetchall()
        results.append((index, rows))
    return results


def print_result(label: str, rows: Iterable[tuple]) -> None:
    rows = list(rows)
    if not rows:
        print(f"{label}: no issues found")
        return

    print(f"{label}:")
    for row in rows:
        print(row)


def main() -> None:
    DB_PATH.unlink(missing_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        bootstrap_database(conn)
        findings = run_validation_queries(conn)

    print(f"Validation database created at: {DB_PATH}")
    for index, rows in findings:
        label = f"Check {index}"
        print_result(label, rows)


if __name__ == "__main__":
    main()
