import re
from typing import Dict, List, Optional
from datetime import datetime

from loguru import logger
from sqlalchemy import asc, desc


def get_filters(combined_filters: Optional[str], filter_mapping: Dict[str, str], default_field: str, date_fields: Optional[List[str]] = None):
    filters = {}
    operator_map = {
        ">": "gt",
        "<": "lt",
        ">=": "gte",
        "<=": "lte",
        "=": "eq",
        "has": "has",
    }

    if combined_filters:
        mini_filters = [
            f.strip() for f in combined_filters.split(",") if f.strip()
        ]
        for mf in mini_filters:
            if " has " in mf.lower():
                parts = re.split(r"\s+has\s+", mf, flags=re.IGNORECASE)
                if len(parts) == 2:
                    field_part = parts[0].strip().title()
                    value_part = parts[1].strip()
                    db_field = filter_mapping.get(field_part)
                    if db_field:
                        filters[f"{db_field}__contains"] = value_part
                continue

            pattern = r"^(?P<field>.*?)\s*(?P<op>>=|<=|>|<|=)\s*(?P<value>.*)$"
            match = re.match(pattern, mf)
            if match:
                field_part = match.group("field").strip().title()
                op_part = match.group("op").strip()
                value_part = match.group("value").strip()
                # Convert True/False to 1/0
                if date_fields and field_part in date_fields:
                    value_part = datetime.strptime(value_part, "%d-%m-%Y").timestamp()
                elif value_part.lower() == "yes":
                    value_part = 1
                elif value_part.lower() == "no":
                    value_part = 0
                db_field = filter_mapping.get(field_part)
                if db_field and op_part in operator_map:
                    op_key = operator_map[op_part]
                    filters[f"{db_field}__{op_key}"] = value_part
            else:
                if search_field := filter_mapping.get(default_field):
                    filters[search_field + "__contains"] = mf
                else:
                    logger.warning(
                        f"Could not find field for search term: {mf}"
                    )
    return filters

def get_sorting(sort: Optional[str], order: Optional[str], sort_mapping: Dict[str, str]):
    order_by = []
    if sort:
        sort_field = sort_mapping.get(sort)
        if sort_field:
            if sort_field:
                if order and order.lower() == "desc":
                    order_by.append(desc(sort_field))
                else:
                    order_by.append(asc(sort_field))
    return order_by