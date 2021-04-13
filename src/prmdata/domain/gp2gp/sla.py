from datetime import timedelta
from enum import Enum, auto

THREE_DAYS_IN_SECONDS = 259200
EIGHT_DAYS_IN_SECONDS = 691200


class SlaBand(Enum):
    WITHIN_3_DAYS = auto()
    WITHIN_8_DAYS = auto()
    BEYOND_8_DAYS = auto()


class SlaCounter:
    def __init__(self):
        self._counts = {
            SlaBand.WITHIN_3_DAYS: 0,
            SlaBand.WITHIN_8_DAYS: 0,
            SlaBand.BEYOND_8_DAYS: 0,
        }

    def increment(self, duration):
        sla_band = assign_to_sla_band(duration)
        self._counts[sla_band] += 1

    def within_3_days(self) -> int:
        return self._counts[SlaBand.WITHIN_3_DAYS]

    def within_8_days(self) -> int:
        return self._counts[SlaBand.WITHIN_8_DAYS]

    def beyond_8_days(self) -> int:
        return self._counts[SlaBand.BEYOND_8_DAYS]

    def total(self) -> int:
        return sum(self._counts.values())


def assign_to_sla_band(sla_duration: timedelta) -> SlaBand:
    sla_duration_in_seconds = sla_duration.total_seconds()
    if sla_duration_in_seconds <= THREE_DAYS_IN_SECONDS:
        return SlaBand.WITHIN_3_DAYS
    elif sla_duration_in_seconds <= EIGHT_DAYS_IN_SECONDS:
        return SlaBand.WITHIN_8_DAYS
    else:
        return SlaBand.BEYOND_8_DAYS
