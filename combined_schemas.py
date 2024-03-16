
from pydantic import BaseModel, validator
from typing import Optional

import shared.sql.schemas as sql_schemas
import shared.mongodb.schemas as mdb_schemas
from shared.mongodb.database import get_db

db = get_db()


class FlightOutput(BaseModel):

    id: int
    number: str
    duration: int
    dep_time: str
    dep_port: mdb_schemas.AirportOutput
    arr_time: str
    arr_port: mdb_schemas.AirportOutput

    class Config:
        orm_mode = True

    @validator("dep_port", "arr_port", pre=True)
    def get_port(cls, value: str):
        return mdb_schemas.AirportOutput(**db.airports.find_one({"iata_code": value.upper()}))
    

class JourneyOutput(sql_schemas.Journey):

    flights: Optional[list[FlightOutput]] = None

    class Config:
        orm_mode = True


class RequestJourneyOutput(sql_schemas.RequestJourney):

    journey_1: JourneyOutput
    journey_2: Optional[JourneyOutput] = None

    class Config:
        orm_mode = True


class RequestOutput(sql_schemas.Request):

    results: Optional[list[RequestJourneyOutput] | dict[str, list[RequestJourneyOutput]]] = None

    class Config:
        orm_mode = True