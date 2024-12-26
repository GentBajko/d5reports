# parsers/file_parser.py

import os
from typing import Set, Dict
from datetime import datetime

import pandas as pd
import polars as pl


class IFileParser:
    """
    Defines a contract for file parsers that extract attendance data from XLSX/XLS.
    """

    def parse_file(self, file_path: str) -> Dict[str, Set[str]]:
        """
        Accepts a path to an XLSX/XLS file and returns a dictionary of date string to set of full names.
        """
        raise NotImplementedError


class FileParser(IFileParser):
    """
    Implementation of the IFileParser interface using Polars for XLSX and Pandas for XLS files.
    """

    def parse_file(self, file_path: str) -> Dict[str, Set[str]]:
        results: Dict[str, Set[str]] = {}
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()

        try:
            if file_extension == ".xlsx":
                # Use Polars for .xlsx files
                df = pd.read_excel(file_path)
            elif file_extension == ".xls":
                # Use Pandas for .xls files with xlrd engine
                df = pd.read_excel(file_path, engine="xlrd")
            else:
                print(f"Unsupported file extension: {file_extension}")
                return results
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return results

        # Ensure required columns are present
        required_columns = ["Date And Time", "First Name", "Last Name"]
        for col in required_columns:
            if col not in df.columns:
                print(f"Missing required column: {col}")
                return results

        # Process each row
        for _, row in df.iterrows():
            dt_str = row.get("Date And Time")
            first_name = str(row.get("First Name", "")).strip()
            last_name = str(row.get("Last Name", "")).strip()

            # Parse the date and time
            if isinstance(dt_str, str):
                try:
                    dt_obj = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        dt_obj = datetime.strptime(dt_str, "%m/%d/%Y %H:%M:%S")
                    except ValueError:
                        print(f"Invalid date format: {dt_str}")
                        continue
            elif isinstance(dt_str, datetime):
                dt_obj = dt_str
            else:
                print(f"Unrecognized date format: {dt_str}")
                continue

            # Combine first and last names
            full_name = f"{first_name} {last_name}".strip()
            if not full_name:
                print(f"Empty full name for row: {row}")
                continue

            # Format the date as YYYY-MM-DD
            date_key = dt_obj.strftime("%Y-%m-%d")

            # Add the full name to the corresponding date
            if date_key not in results:
                results[date_key] = set()
            results[date_key].add(full_name)
        print(results)

        return results
