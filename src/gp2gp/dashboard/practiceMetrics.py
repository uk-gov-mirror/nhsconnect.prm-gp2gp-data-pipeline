from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List

from dateutil.tz import tzutc

from gp2gp.service.practiceMetrics import PracticeSlaMetrics


@dataclass
class TimeToIntegrateSla:
    within_3_days: int
    within_8_days: int
    beyond_8_days: int


@dataclass
class RequesterMetrics:
    time_to_integrate_sla: TimeToIntegrateSla


@dataclass
class MonthlyMetrics:
    year: int
    month: int
    requester: RequesterMetrics


@dataclass
class PracticeSummary:
    ods_code: str
    name: str
    metrics: List[MonthlyMetrics]


@dataclass
class ServiceDashboardData:
    generated_on: datetime
    practices: List[PracticeSummary]


def construct_service_dashboard_data(
    sla_metrics: Iterable[PracticeSlaMetrics], year: int, month: int
) -> ServiceDashboardData:

    return ServiceDashboardData(
        generated_on=datetime.now(tzutc()),
        practices=[
            PracticeSummary(
                ods_code=practice.ods_code,
                name=practice.name,
                metrics=[
                    MonthlyMetrics(
                        year=year,
                        month=month,
                        requester=RequesterMetrics(
                            time_to_integrate_sla=TimeToIntegrateSla(
                                within_3_days=practice.within_3_days,
                                within_8_days=practice.within_8_days,
                                beyond_8_days=practice.beyond_8_days,
                            )
                        ),
                    )
                ],
            )
            for practice in sla_metrics
        ],
    )
