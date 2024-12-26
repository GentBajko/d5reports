from io import BytesIO
import os
from typing import Optional, Set, Dict
from datetime import datetime

from loguru import logger
import pandas as pd


class IFileParser:
    """
    Defines a contract for file parsers that extract attendance data from XLS/XLSX content.
    """

    def parse_file(self, file_path: str) -> Dict[str, Set[str]]:
        """
        Accepts a path to an XLS/XLSX file on disk and returns a dictionary of
        date string to set of full names.
        """
        raise NotImplementedError

    def parse_bytes(
        self, file_content: bytes, file_extension: str
    ) -> Dict[str, Set[str]]:
        """
        Accepts raw XLS/XLSX file content and its extension, returning a dictionary
        of date string to set of full names.
        """
        raise NotImplementedError


class FileParser(IFileParser):
    """
    Implementation of the IFileParser interface using Pandas for XLS/XLSX files.
    """

    def parse_file(self, file_path: str) -> Dict[str, Set[str]]:
        """
        Accepts a path to an XLS/XLSX file on disk and returns a dictionary
        of date string to set of full names.
        """
        results: Dict[str, Set[str]] = {}
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()
        try:
            if file_extension == ".xlsx":
                df = pd.read_excel(file_path)
            elif file_extension == ".xls":
                df = pd.read_excel(file_path, engine="xlrd")
            else:
                return results
        except Exception:
            return results
        required_columns = ["Date And Time", "First Name", "Last Name"]
        for col in required_columns:
            if col not in df.columns:
                return results
        for _, row in df.iterrows():
            dt_str = row.get("Date And Time")
            first_name = str(row.get("First Name", "")).strip()
            last_name = str(row.get("Last Name", "")).strip()
            dt_obj = self._parse_date(dt_str)
            if not dt_obj:
                continue
            full_name = f"{first_name} {last_name}".strip()
            if not full_name:
                continue
            date_key = dt_obj.strftime("%Y-%m-%d")
            if date_key not in results:
                results[date_key] = set()
            results[date_key].add(full_name)
        return results

    def parse_bytes(
        self, file_content: bytes, file_extension: str
    ) -> Dict[str, Set[str]]:
        """
        Accepts raw XLS/XLSX file content and its extension, returning a dictionary
        of date string to set of full names.
        """
        results: Dict[str, Set[str]] = {}
        file_extension = file_extension.lower()
        try:
            if file_extension == "xlsx":
                df = pd.read_excel(BytesIO(file_content))
            elif file_extension == "xls":
                df = pd.read_excel(BytesIO(file_content), engine="xlrd")
            else:
                return results
        except Exception as e:
            logger.exception(e)
            return results
        required_columns = ["Date And Time", "First Name", "Last Name"]
        for col in required_columns:
            if col not in df.columns:
                return results
        for _, row in df.iterrows():
            dt_str = row.get("Date And Time")
            first_name = str(row.get("First Name", "")).strip()
            last_name = str(row.get("Last Name", "")).strip()
            dt_obj = self._parse_date(dt_str)
            if not dt_obj:
                continue
            full_name = f"{first_name} {last_name}".strip()
            if not full_name:
                continue
            date_key = dt_obj.strftime("%Y-%m-%d")
            if date_key not in results:
                results[date_key] = set()
            results[date_key].add(full_name)
        return results

    def _parse_date(self, dt_value) -> Optional[datetime]:
        """
        Internal helper that parses the date field into a datetime object.
        """
        if isinstance(dt_value, datetime):
            return dt_value
        if isinstance(dt_value, str):
            for fmt in ("%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M:%S"):
                try:
                    return datetime.strptime(dt_value, fmt)
                except ValueError:
                    pass
        return None
