from sqlmodel import SQLModel, Field

ID_REGEX = r'^$'
"""
TODO: id regex
"""


class Agency(SQLModel, table=True):
    agency_id: str = Field(primary_key=True, nullable=False)
    agency_name: str = Field(nullable=False)
    agency_url: str = Field(nullable=False)
    agency_timezone: str = Field(
        nullable=False, const=True, default="Europe/Paris"
    )
    agency_lang: str
    agency_phone: str
    agency_email: str
    agency_fare_url: str


class Calendar_Date(SQLModel, table=True):

    service_id: str = Field(nullable=False)
    """
    TODO: Chose where to put the primary key
    """

    date: int = Field(nullable=False)
    """
    TODO: Date in YYYYMMDD format
    """

    exception_type: int = Field(nullable=False)
    """
    TODO: 1 when POSITIVE, 2 when NEGATIVE
    """


class Calendar(SQLModel, table=True):

    service_id = Field(nullable=False)
    """
    TODO: Chose where to put the primary key
    """

    monday: int = Field(nullable=False, ge=0, le=1)
    """
    ! BE CAREFUL !

    - 0 == "Service Disponible"
    - 1 == "Service Indisponible"
    """
    tuesday: int = Field(nullable=False, ge=0, le=1)
    """
    ! BE CAREFUL !

    - 0 == "Service Disponible"
    - 1 == "Service Indisponible"
    """
    wednesday: int = Field(nullable=False, ge=0, le=1)
    """
    ! BE CAREFUL !

    - 0 == "Service Disponible"
    - 1 == "Service Indisponible"
    """
    thursday: int = Field(nullable=False, ge=0, le=1)
    """
    ! BE CAREFUL !

    - 0 == "Service Disponible"
    - 1 == "Service Indisponible"
    """
    friday: int = Field(nullable=False, ge=0, le=1)
    """
    ! BE CAREFUL !

    - 0 == "Service Disponible"
    - 1 == "Service Indisponible"
    """
    saturday: int = Field(nullable=False, ge=0, le=1)
    """
    ! BE CAREFUL !

    - 0 == "Service Disponible"
    - 1 == "Service Indisponible"
    """
    sunday: int = Field(nullable=False, ge=0, le=1)
    """
    ! BE CAREFUL !

    - 0 == "Service Disponible"
    - 1 == "Service Indisponible"
    """

    start_date: str = Field(nullable=False)
    """
    TODO: Date in YYYYMMDD format
    """

    end_date: str = Field(nullable=False)
    """
    TODO: Date in YYYYMMDD format
    """


class Pathway(SQLModel, table=True):
    pathway_id: str = Field(primary_key=True, nullable=False)
    from_stop_id: str = Field(foreign_key="Stop.stop_id", nullable=False)
    to_stop_id: str = Field(foreign_key="Stop.stop_id", nullable=False)
    pathway_mode: int = Field(nullable=False, ge=1, le=6)
    is_bidirectional: bool = Field(nullable=False)
    length: float = Field(ge=0)
    traversal_time: int = Field(ge=0)
    stair_count: int = Field(ge=0)
    max_slope: float
    min_width: float
    signposted_as: str
    reversed_signposted_as: str


class Route(SQLModel, table=True):
    HEXA_REGEX = r'^[0-9A-Fa-f]{6}$'

    route_id: str = Field(primary_key=True, nullable=False)
    agency_id: str = Field(foreign_key="Agency.id", nullable=False)
    route_short_name: str = Field(max_length=9, nullable=False)
    route_long_name: str = Field(nullable=False)
    route_desc: str
    route_type: int = Field(nullable=False, ge=0, le=7)
    route_url: str
    route_color: str = Field(min_length=6, max_length=6,
                             regex=HEXA_REGEX, default="000000")
    route_text_color: str = Field(
        min_length=6, max_length=6, regex=HEXA_REGEX, default="FFFFFF")
    route_sort_order: int = Field(ge=0)


class Stop_Extension(SQLModel, table=True):
    object_id: str = Field(nullable=False)
    object_system: str
    object_code: str


class Stop_Time(SQLModel, table=True):
    TIME_REGEX = r'^\d{2}:\d{2}:\d{2}$'

    trip_id: str = Field(foreign_key="Trip.trip_id", nullable=False)
    arrival_time: str = Field(nullable=False, regex=TIME_REGEX)
    departure_time: str = Field(nullable=False, regex=TIME_REGEX)
    stop_id: str = Field(foreign_key="Stop.stop_id", nullable=False)
    stop_sequence: int = Field(nullable=False, ge=0)
    pickup_type: bool
    drop_off_type: bool
    local_zone_id: str
    stop_headsign: str
    timepoint: bool


class Stop(SQLModel, table=True):
    stop_id: str = Field(primary_key=True, nullable=False, )
    stop_code: str
    stop_name: str = Field(nullable=False)
    stop_desc: str
    stop_lon: float = Field(nullable=False)
    stop_lat: float = Field(nullable=False)
    zone_id: int = Field(nullable=False, ge=1, le=101)
    stop_url: str
    location_type: int = Field(ge=0, le=2)
    parent_station: str = Field(foreign_key="Stop.stop_id", nullable=False)
    wheelchair_boarding: int = Field(ge=0, le=2)
    stop_timezone: str
    level_id: int
    platform_code: str


class Transfer(SQLModel, table=True):
    from_stop_id: str = Field(foreign_key="Stop.stop_id", nullable=False)
    to_stop_id: str = Field(foreign_key="Stop.stop_id", nullable=False)
    transfer_type: int = Field(nullable=False)
    min_transfer_time: int = Field(ge=0)


class Trip(SQLModel, table=True):
    route_id: str = Field(foreign_key="Route.route_id", nullable=False)

    service_id: str = Field(nullable=False)
    """
    TODO: Chose where to put the primary key
    """

    trip_id: str = Field(primary_key=True, nullable=False)
    trip_headsign: str
    trip_short_name: str
    direction_id: int = Field(ge=0, le=1)

    block_id: str
    """
    No idea what this refers to
    """

    shape_id: str = Field(nullable=False)
    wheelchair_accessible: int = Field(ge=0, le=2)
    bikes_allowed: int = Field(ge=0, le=2)
