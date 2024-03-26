from typing import Any, Optional, Union
from pydantic import BaseModel, root_validator, validator


class TotalRoutes(BaseModel):
    num_flights: int

    class Config:
        orm_mode = True


class Route(BaseModel):
    airline_iata: Optional[str]
    airline_icao: Optional[str]
    flight_number: Optional[str]
    flight_iata: Optional[str]
    flight_icao: Optional[str]
    dep_iata: Optional[str]
    dep_icao: Optional[str]
    dep_time_utc: Optional[str]
    dep_time: Optional[str]
    arr_iata: Optional[str]
    arr_icao: Optional[str]
    arr_time_utc: Optional[str]
    arr_time: Optional[str]
    duration: Optional[int]
    days: Optional[list[int]]
    aircraft_icao: Optional[str]
    updated: Optional[str]

    @root_validator(pre=True)
    def root_validate(cls, values):
        icao = values.get("flight_icao")
        iata = values.get("flight_iata")

        if not any((icao, iata)):
            raise ValueError("At least one of flight_iata or flight_icao must be specified.")

        return values

    @validator("days", pre=True)
    def days_validate(cls, values):
        mapping = {"sun": 0, "mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6}
        return [mapping[val] if not isinstance(val, int) else val for val in values]


class Location(BaseModel):
    type: str = "Point"
    coordinates: list[float]


class Distance(BaseModel):
    calculated: float


class Airport(BaseModel):
    iata_code: Optional[str]
    icao_code: Optional[str]
    name: Optional[str]
    country_code: Optional[str]
    location: Optional[Location]

    @root_validator(pre=True)
    def root_validate(cls, values):
        icao = values.get("icao_code")
        iata = values.get("iata_code")

        if not any((icao, iata)):
            raise ValueError("At least one of icao_code or iata_code must be specified.")

        return values


class AirportOutput(Airport):

    # Derived, not present in raw data
    num_dep: Optional[int] = None
    num_arr: Optional[int] = None

    class Config:
        orm_mode = True


class AirportDistOutput(AirportOutput):
    
    dist: Distance

    class Config:
        orm_mode = True


class NumAirportConnectionsOutput(BaseModel):

    num_dep_links: int
    num_arr_links: int
    connection: Union[Airport, str]  # If airport not found in database, output identifier instead

    class Config:
        orm_mode = True


class AirportConnectionsOutput(AirportOutput):

    dep_links: list[Route]
    arr_links: list[Route]

    class Config:
        orm_mode = True