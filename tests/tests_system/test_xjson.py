import datetime

import pytest

from app.utils.xjson import XJSONEncoder, dumps, loads, xjson_decoder


@pytest.fixture()
def date_time() -> datetime.datetime:
    return datetime.datetime(2022, 9, 19, 9, 30, 15)


def test_xjson_decoder(date_time: datetime.datetime) -> None:
    datetime_obj = {
        "__type__": "__datetime__",
        "isoformat": date_time.isoformat(),
    }
    assert xjson_decoder(datetime_obj) == date_time
    now_date = date_time.date()
    date_obj = {
        "__type__": "__date__",
        "isoformat": now_date.isoformat(),
    }
    assert xjson_decoder(date_obj) == now_date
    assert xjson_decoder([1]) == [1]


def test_xjson_encoder(date_time: datetime.datetime) -> None:
    encoder = XJSONEncoder()
    now_date = date_time.date()
    assert dict(encoder.default(date_time)) == {"__type__": "__datetime__", "isoformat": "2022-09-19T09:30:15"}
    assert dict(encoder.default(now_date)) == {"__type__": "__date__", "isoformat": "2022-09-19"}
    with pytest.raises(TypeError):
        encoder.default({})


def test_dumps(date_time: datetime.datetime) -> None:
    assert dumps(date_time) == '{"__type__": "__datetime__", "isoformat": "2022-09-19T09:30:15"}'
    assert dumps(1) == "1"


def test_loads(date_time: datetime.datetime) -> None:
    assert loads('{"__type__": "__datetime__", "isoformat": "2022-09-19T09:30:15"}') == date_time
