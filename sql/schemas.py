import logging
from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, FutureDate, root_validator, validator

from packages.config import global_settings, paths
from packages.shared.utils import types
from packages.shared.utils.dates import time_from_string

FLEXIBILITY = {1: "flexible-1day", 2: "flexible-2days", 3: "flexible-3days"}

SORT_OPTIONS = {0: "bestflight", 1: "price", 2: "duration"}


class RequestBase(BaseModel):
    dep_port: types.IataLonExample
    arr_port: types.IataIstExample
    dep_date: types.Date
    ret_date: Optional[types.Date] = None
    flex_option: int = 0
    sorted_by: Optional[str] = SORT_OPTIONS[0]
    direct: Optional[bool] = False

    @validator("dep_date", "ret_date", pre=True)
    def date_validate(cls, value):
        if value is not None:
            if isinstance(value, str):
                value = datetime.strptime(value, global_settings.date_fmt).date()

            elif not isinstance(value, date):
                raise ValueError("Value must be type: datetime.date or date string")

        return value

    @validator("flex_option", pre=True)
    def flex_option_validate(cls, value):
        if value:
            validate_mapping(FLEXIBILITY, value)

        return value

    @validator("sorted_by", pre=True)
    def sort_by_validate(cls, value):
        return validate_mapping(SORT_OPTIONS, value)

    @root_validator()
    def date_increase_validate(cls, values):
        dep_date = values.get("dep_date")
        ret_date = values.get("ret_date", None)

        if ret_date is not None:
            if dep_date > ret_date:
                raise ValueError(
                    f"ret_date must be greater than or equal to dep_date: {ret_date} !> {values['dep_date']}"
                )

        return values

    def get_url(self):
        def get_date_str(d: types.Date):
            d_str = d.strftime(global_settings.date_fmt)
            if self.flex_option:
                d_str += f"-{FLEXIBILITY[self.flex_option]}"

            return d_str

        def sort_format(sort_str):
            return f"bestflight_a?sort={sort_str}_a"

        dep_date = get_date_str(self.dep_date)
        request_url = f"{self.dep_port}-{self.arr_port}/{dep_date}/"

        if self.ret_date:
            ret_date = get_date_str(self.ret_date)
            request_url += ret_date

        request_url += sort_format(self.sorted_by)

        if self.direct:
            request_url += "&fs=stops=0"

        return request_url


class FlightBase(BaseModel):
    number: str
    duration: int
    dep_time: str
    dep_port: str
    arr_time: str
    arr_port: str

    @validator("duration", pre=True)
    def duration_validate(cls, value):
        if isinstance(value, str):
            value = time_from_string(value).seconds / 60

        return value

    @validator("number", "dep_port", "arr_port")
    def truncate_validator(cls, value: str):
        return value[:30]


class JourneyBase(BaseModel):
    date: date
    day: int
    duration: int
    dep_port: str
    dep_time: str
    arr_port: str
    arr_time: str
    arr_day_offset: int
    airline: str
    stops: int
    stop_city: Optional[str] = None
    flights: Optional[list[FlightBase]] = None

    @validator("duration", pre=True)
    def duration_validate(cls, value):
        if isinstance(value, str):
            value = time_from_string(value).seconds / 60

        return value


class RequestJourneyBase(BaseModel):
    request_id: int
    journey_id_1: int
    journey_id_2: Optional[int] = None
    price: int
    currency: str = "USD"


class JourneyFlightBase(BaseModel):
    journey_id: int
    flight_id: int


class RequestCreate(RequestBase):
    dep_date: FutureDate
    ret_date: Optional[FutureDate] = None
    # use_proxy: Optional[bool] = False
    pass


class RequestJourneyCreate(RequestJourneyBase):
    pass


class JourneyFlightCreate(JourneyFlightBase):
    pass


class Request(RequestBase):
    id: int
    status: Optional[str] = None
    timestamp: datetime

    class Config:
        orm_mode = True

    def get_date(self) -> date:
        return self.timestamp.date()

    def get_date_str(self):
        return self.get_date().strftime(global_settings.date_fmt)

    def get_dir(self) -> str:
        params = [
            self.dep_port,
            self.arr_port,
            self.dep_date.strftime(global_settings.date_fmt),
            self.sorted_by,
        ]
        if self.ret_date:
            params.insert(3, self.ret_date.strftime(global_settings.date_fmt))
        if self.flex_option:
            params.append(FLEXIBILITY[self.flex_option])
        if self.id is not None:
            params.append(f"id{self.id}")

        stem = "-".join(params)

        return stem

    def get_save_path(self):
        return paths.data_path / self.get_date_str() / self.get_dir()

    def adapt_logger(self, logger):
        return RequestAdapter(logger, {"id": self.id})


class RequestAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        if self.extra is None:
            raise ValueError("Adapter must be initialized with extra dict")

        return "[Request: %s] %s" % (self.extra["id"], msg), kwargs


class Journey(JourneyBase):
    id: int

    class Config:
        orm_mode = True


class Flight(FlightBase):
    id: int

    class Config:
        orm_mode = True


class RequestJourney(RequestJourneyBase):
    id: int

    class Config:
        orm_mode = True


class JourneyFlight(JourneyFlightBase):
    id: int

    class Config:
        orm_mode = True


class FlightOutput(Flight):
    class Config:
        orm_mode = True


class JourneyOutput(Journey):
    flights: Optional[list[FlightOutput]] = None

    class Config:
        orm_mode = True


class TripBase(BaseModel):
    price: int
    currency: str = "USD"
    # request: Optional[Request] = None
    journey_1: JourneyBase
    journey_2: Optional[JourneyBase] = None


class TripOutput(TripBase):
    class Config:
        orm_mode = True


class RequestJourneyOutput(RequestJourney):
    journey_1: JourneyOutput
    journey_2: Optional[JourneyOutput] = None

    class Config:
        orm_mode = True


class RequestOutput(Request):
    results: Optional[list[RequestJourneyOutput]] = None

    class Config:
        orm_mode = True


class PriceSummary(BaseModel):
    request_id: int
    min: int
    avg: int

    class Config:
        orm_mode = True


def validate_mapping(d: dict[Any, Any], key_or_value):
    if key_or_value in d.keys():
        v = d[key_or_value]
    elif key_or_value in d.values():
        v = key_or_value
    else:
        raise ValueError(
            f"Input must be either key to map to value, or value directly from: {d}"
        )

    return v
