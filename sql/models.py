import sqlalchemy as sql
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql.expression import func
from shared.sql.database import Base


def truncate_string(*fields):
    class TruncateStringMixin:
        @validates(*fields)
        def validate_string_field_length(self, key, value):
            max_len = getattr(self.__class__, key).prop.columns[0].type.length
            if value and len(value) > max_len:
                return value[:max_len]
            return value

    return TruncateStringMixin


class Request(Base):
    __tablename__ = "request"

    id = sql.Column(sql.Integer, primary_key=True)
    status = sql.Column(sql.String(20), nullable=True)
    dep_date = sql.Column(sql.Date)
    ret_date = sql.Column(sql.Date, nullable=True)
    dep_port = sql.Column(sql.String(20))  # Large to allow multiple IATA codes to be specified.
    arr_port = sql.Column(sql.String(20))
    flex_option = sql.Column(sql.Integer)
    sorted_by = sql.Column(sql.String(30))
    direct = sql.Column(sql.Boolean)
    timestamp = sql.Column(sql.TIMESTAMP(timezone=False), server_default=func.now())

    results = relationship("RequestJourney", back_populates="request", lazy="joined")


class Journey(Base):
    __tablename__ = "journey"

    id = sql.Column(sql.Integer, primary_key=True)
    date = sql.Column(sql.Date)
    day = sql.Column(sql.Integer)
    duration = sql.Column(sql.Integer)
    dep_port = sql.Column(sql.String(3))
    dep_time = sql.Column(sql.String(10))
    arr_port = sql.Column(sql.String(3))
    arr_time = sql.Column(sql.String(10))
    stops = sql.Column(sql.Integer)
    stop_city = sql.Column(sql.String(30), nullable=True)
    airline = sql.Column(sql.String(40))

    flights = relationship("Flight", secondary="journey_flight", lazy="joined")


class RequestJourney(Base):
    __tablename__ = "request_journey"

    id = sql.Column(sql.Integer, primary_key=True)
    # TODO: Unique constraint?
    request_id = sql.Column(sql.ForeignKey("request.id"))
    journey_id_1 = sql.Column(sql.ForeignKey("journey.id"))
    journey_id_2 = sql.Column(sql.ForeignKey("journey.id"), nullable=True)

    price = sql.Column(sql.Integer)
    currency = sql.Column(sql.String(3), default="USD")

    request = relationship("Request", back_populates="results")
    journey_1 = relationship("Journey", foreign_keys=[journey_id_1], lazy="joined")
    journey_2 = relationship("Journey", foreign_keys=[journey_id_2], lazy="joined")

# Not currently in use since get_or_add will see non-truncated schemas as new model entries.
# class Flight(Base, truncate_string("number", "dep_port", "arr_port")):


class Flight(Base):
    __tablename__ = "flight"

    id = sql.Column(sql.Integer, primary_key=True)
    number = sql.Column(sql.String(30))
    duration = sql.Column(sql.Integer)
    dep_port = sql.Column(sql.String(30))
    dep_time = sql.Column(sql.String(10))
    arr_port = sql.Column(sql.String(30))
    arr_time = sql.Column(sql.String(10))


class JourneyFlight(Base):
    __tablename__ = "journey_flight"

    journey_id = sql.Column(sql.ForeignKey("journey.id"), primary_key=True)
    flight_id = sql.Column(sql.ForeignKey("flight.id"), primary_key=True)


"""
class BestPrice(Base):
    __tablename__ = "bestprice"

    id = sql.Column(sql.Integer, primary_key=True)
    request_id = sql.Column(sql.Integer, sql.ForeignKey("request.id"), nullable=False)
    dep_date = sql.Column(sql.Date)
    ret_date = sql.Column(sql.Date, nullable=True)
    price = sql.Column(sql.Integer)
"""