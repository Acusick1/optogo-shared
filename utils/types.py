from datetime import date
from typing import Annotated, Literal, Optional

from fastapi import Depends, Path, Query
from packages.config import settings
from pydantic import BaseModel

IataLonExample = Annotated[
    str,
    Query(
        examples=["LHR"],
        min_length=3,
        max_length=3,
        description="Airport 3 letter IATA code.",
    ),
]
IataIstExample = Annotated[
    str,
    Query(
        examples=["IST"],
        min_length=3,
        max_length=3,
        description="Airport 3 letter IATA code.",
    ),
]

MultiIataLonExample = Annotated[
    list[str],
    Query(examples=[["LHR", "LGW"]], description="List of airport IATA codes."),
]
MultiIataBcnExample = Annotated[
    list[str],
    Query(examples=[["MAD", "BCN"]], description="List of airport IATA codes."),
]

AirportMinRoutes = Annotated[
    int, Query(description="Minimum number of routes required to include in response.")
]

CountryCode = Annotated[
    str,
    Query(
        examples=["GB"],
        min_length=2,
        max_length=2,
        description="2 letter country code.",
    ),
]

Date = Annotated[
    date,
    Query(examples=[date.today()], description="Date in the format 'YYYY-MM-DD'."),
]
Days = Annotated[
    list[int],
    Query(
        ge=0,
        le=6,
        examples=[[5, 6]],
        description="Days of the week (0 is Sunday), for any day leave empty.",
    ),
]
Flexibility = Annotated[
    int, Query(ge=0, description="Number of days either side of input date.")
]
GroupRoutes = Annotated[
    bool, Query(description="Group results by route taken (airports).")
]

Idx = Annotated[int, Path(ge=0, description="Database ID")]
# TODO: once pydantic upgraded to >2.0, try using a functional_validator to convert from str2int before Literal
SortOrder = Annotated[
    Literal["1", "-1"], Query(description="Sort ascending (1) or descending (-1).")
]
Limit = Annotated[
    int,
    Query(le=settings.return_limit, description="Maximum number of records to return."),
]
Page = Annotated[
    int,
    Query(
        ge=0,
        description="Returned paginated results, used in conjunction with limit to skip records.",
    ),
]

GenericSortBy = Annotated[
    str,
    Query(description="Return field to sort by (see respose output for fields)."),
]
FlightSortBy = Annotated[
    str,
    Query(
        examples=["dep_time"],
        description="Return field to sort by (see respose output for fields).",
    ),
]
AirportSortBy = Annotated[
    str,
    Query(
        examples=["iata_code"],
        description="Return field to sort by (see respose output for fields).",
    ),
]
LocationSortBy = Annotated[
    str,
    Query(
        description="Return field to sort by, default = calculated distance (see respose output for other fields)."
    ),
]


# TODO: Can we change defaults/examples within these for a specific endpoint i.e. resetting "example"?
class CommonQueryParams(BaseModel):
    sort_by: Optional[GenericSortBy] = None
    sort_order: SortOrder = "1"
    limit: Limit = settings.return_limit
    page: Page = 0


class CommonFlightQueryParams(CommonQueryParams):
    sort_by: Optional[FlightSortBy] = None


class CommonAirportQueryParams(CommonQueryParams):
    sort_by: Optional[AirportSortBy] = None


class CommonLocationQueryParams(CommonAirportQueryParams):
    sort_by: Optional[LocationSortBy] = None


Commons = Annotated[CommonQueryParams, Depends()]
FlightCommons = Annotated[CommonFlightQueryParams, Depends()]
AirportCommons = Annotated[CommonAirportQueryParams, Depends()]
LocationCommons = Annotated[CommonLocationQueryParams, Depends()]
