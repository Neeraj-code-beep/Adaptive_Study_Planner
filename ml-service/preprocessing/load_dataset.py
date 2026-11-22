"""
Dataset Loading Module
File: ml-service/preprocessing/load_dataset.py

Responsible for reading raw CSV datasets safely with explicit encoding,
handling malformed rows, and providing an iterator or in-memory list
without modifying the original file.
"""

import os
import csv
from typing import Iterator, Dict, List, Tuple

def load_raw_dataset_stream(
    file_path: str,
    encoding: str = "ISO-8859-1"
) -> Tuple[List[str], Iterator[Dict[str, str]]]:
    """
    Streams interaction records from the raw CSV file.
    Yields (header, row_dict_iterator). Closes file handle safely.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Raw dataset file not found: {file_path}")

    f = open(file_path, mode="r", encoding=encoding, errors="replace")
    reader = csv.reader(f)
    try:
        header = next(reader)
    except StopIteration:
        f.close()
        raise ValueError(f"Empty dataset file: {file_path}")
    except Exception:
        f.close()
        raise

    header = [h.strip() for h in header]

    def record_generator() -> Iterator[Dict[str, str]]:
        try:
            for line_no, row in enumerate(reader, start=2):
                if not row:
                    continue
                # Handle row length mismatches safely
                if len(row) < len(header):
                    row = row + [""] * (len(header) - len(row))
                elif len(row) > len(header):
                    row = row[:len(header)]
                yield {header[i]: row[i].strip() for i in range(len(header))}
        finally:
            if not f.closed:
                f.close()

    return header, record_generator()

def load_raw_dataset_memory(
    file_path: str,
    encoding: str = "ISO-8859-1",
    max_rows: int = None
) -> Tuple[List[str], List[Dict[str, str]]]:
    """
    Loads raw CSV records into memory as a list of dictionaries.
    Optional max_rows parameter for testing/profiling.
    """
    header, stream = load_raw_dataset_stream(file_path, encoding=encoding)
    records = []
    for i, rec in enumerate(stream):
        if max_rows is not None and i >= max_rows:
            break
        records.append(rec)
    return header, records
