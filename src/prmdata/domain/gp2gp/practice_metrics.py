from warnings import warn
from typing import NamedTuple, Iterable, Iterator, Set

from prmdata.domain.gp2gp.practice_lookup import PracticeLookup
from prmdata.domain.gp2gp.transfer import Transfer
from prmdata.domain.gp2gp.sla import SlaCounter


class IntegratedPracticeMetrics(NamedTuple):
    transfer_count: int
    within_3_days: int
    within_8_days: int
    beyond_8_days: int


class PracticeMetrics(NamedTuple):
    ods_code: str
    name: str
    integrated: IntegratedPracticeMetrics


class PracticeSlaCounter:
    def __init__(self, practice_lookup: PracticeLookup):
        self._lookup = practice_lookup
        self._sla_counts = {
            practice.ods_code: SlaCounter() for practice in practice_lookup.all_practices()
        }
        self._unexpected_asids: Set[str] = set()

    def increment(self, asid, duration):
        if self._lookup.has_asid_code(asid):
            ods_code = self._lookup.ods_code_from_asid(asid)
            self._sla_counts[ods_code].increment(duration)
        else:
            self._unexpected_asids.add(asid)

    def results(self) -> Iterator[PracticeMetrics]:
        return (
            self._derive_practice_sla_metrics(practice) for practice in self._lookup.all_practices()
        )

    def _derive_practice_sla_metrics(self, practice):
        sla_metrics = self._sla_counts[practice.ods_code]
        return PracticeMetrics(
            practice.ods_code,
            practice.name,
            integrated=IntegratedPracticeMetrics(
                transfer_count=sla_metrics.total(),
                within_3_days=sla_metrics.within_3_days(),
                within_8_days=sla_metrics.within_8_days(),
                beyond_8_days=sla_metrics.beyond_8_days(),
            ),
        )

    def unexpected_asid_codes(self) -> Set[str]:
        return self._unexpected_asids


def calculate_sla_by_practice(
    practice_lookup: PracticeLookup, transfers: Iterable[Transfer]
) -> Iterator[PracticeMetrics]:
    per_practice_sla_counter = PracticeSlaCounter(practice_lookup)

    for transfer in transfers:
        per_practice_sla_counter.increment(transfer.requesting_practice_asid, transfer.sla_duration)

    unexpected_asid_codes = per_practice_sla_counter.unexpected_asid_codes()
    if len(unexpected_asid_codes) > 0:
        warn(f"Unexpected ASID count: {len(unexpected_asid_codes)}", RuntimeWarning)

    return per_practice_sla_counter.results()
