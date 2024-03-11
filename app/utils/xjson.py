import json
from collections import OrderedDict
from datetime import date, datetime
from typing import Any

from dateutil.parser import parse as parse_date


class XJSONEncoder(json.JSONEncoder):
    """JSONEncoder that supports encoding to JSON various complex types."""

    def default(self, obj: Any) -> Any | dict[str, str]:
        match obj:
            case datetime():
                return OrderedDict(
                    (
                        ("__type__", "__datetime__"),
                        ("isoformat", obj.isoformat()),
                    ),
                )
            case date():
                return OrderedDict(
                    (
                        ("__type__", "__date__"),
                        ("isoformat", obj.isoformat()),
                    ),
                )
            case _:
                return super().default(obj)


def xjson_decoder(obj: Any) -> Any:
    if "__type__" in obj:
        match obj["__type__"]:
            case "__datetime__":
                return parse_date(obj["isoformat"])
            case "__date__":
                return parse_date(obj["isoformat"]).date()
    return obj


def dumps(obj: Any) -> str:
    return json.dumps(obj, cls=XJSONEncoder)


def loads(obj: str) -> Any:
    return json.loads(obj, object_hook=xjson_decoder)
