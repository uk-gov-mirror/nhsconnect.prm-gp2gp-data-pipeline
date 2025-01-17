import datetime

import pytest

from prmdata.domain.gp2gp.sla import EIGHT_DAYS_IN_SECONDS, THREE_DAYS_IN_SECONDS
from prmdata.domain.gp2gp.national_metrics import calculate_national_metrics
from tests.builders.gp2gp import (
    build_transfers,
    a_pending_transfer,
    a_pending_with_error_transfer,
    an_integrated_transfer,
    a_failed_transfer,
)
from tests.builders.common import an_integer


def test_returns_initiated_transfer_count_default_given_no_transfers():
    national_metrics = calculate_national_metrics([])
    assert national_metrics.initiated_transfer_count == 0


def test_returns_initiated_transfer_count():
    initiated_transfer_count = an_integer(2, 10)
    transfers = build_transfers(transfer_count=initiated_transfer_count)
    national_metrics = calculate_national_metrics(transfers)
    assert national_metrics.initiated_transfer_count == initiated_transfer_count


def test_returns_integrated_transfer_count_defaults_given_no_successful_transfers():
    transfer_count = an_integer(2, 10)
    transfers = build_transfers(transfer_count=transfer_count)
    national_metrics = calculate_national_metrics(transfers)
    assert national_metrics.integrated.transfer_count == 0
    assert national_metrics.integrated.within_3_days == 0
    assert national_metrics.integrated.within_8_days == 0
    assert national_metrics.integrated.beyond_8_days == 0


def test_returns_integrated_transfer_count():
    transfer_count = an_integer(7, 10)
    integrated_transfer_count = an_integer(2, 4)
    transfers = build_transfers(
        transfer_count=transfer_count, integrated_transfer_count=integrated_transfer_count
    )
    national_metrics = calculate_national_metrics(transfers)
    assert national_metrics.integrated.transfer_count == integrated_transfer_count


@pytest.mark.parametrize(
    "sla_duration, expected",
    [
        (
            datetime.timedelta(seconds=THREE_DAYS_IN_SECONDS - 1),
            {"within_3_days": 2, "within_8_days": 0, "beyond_8_days": 0},
        ),
        (
            datetime.timedelta(seconds=EIGHT_DAYS_IN_SECONDS),
            {"within_3_days": 0, "within_8_days": 2, "beyond_8_days": 0},
        ),
        (
            datetime.timedelta(seconds=EIGHT_DAYS_IN_SECONDS + 1),
            {"within_3_days": 0, "within_8_days": 0, "beyond_8_days": 2},
        ),
    ],
)
def test_returns_integrated_transfer_count_by_sla_duration(sla_duration, expected):
    transfer_count = an_integer(7, 10)
    integrated_transfer_count = 2
    transfers = build_transfers(
        transfer_count=transfer_count,
        integrated_transfer_count=integrated_transfer_count,
        sla_duration=sla_duration,
    )
    national_metrics = calculate_national_metrics(transfers)
    assert national_metrics.integrated.within_3_days == expected["within_3_days"]
    assert national_metrics.integrated.within_8_days == expected["within_8_days"]
    assert national_metrics.integrated.beyond_8_days == expected["beyond_8_days"]


def test_returns_failed_transfer_count_default_given_no_transfers():
    national_metrics = calculate_national_metrics([])
    assert national_metrics.failed_transfer_count == 0


def test_returns_failed_transfer_count():
    transfer_count = an_integer(7, 10)
    failed_transfer_count = an_integer(2, 4)
    transfers = build_transfers(
        transfer_count=transfer_count, failed_transfer_count=failed_transfer_count
    )
    national_metrics = calculate_national_metrics(transfers)
    assert national_metrics.failed_transfer_count == failed_transfer_count


def test_returns_pending_transfer_count_default_given_no_transfers():
    transfers = []

    national_metrics = calculate_national_metrics(transfers)

    expected_pending_transfer_count = 0

    assert national_metrics.pending_transfer_count == expected_pending_transfer_count


def test_returns_pending_transfer_count_given_only_pending_transfers():
    transfers = [a_pending_transfer(), a_pending_transfer()]

    national_metrics = calculate_national_metrics(transfers)

    expected_pending_transfer_count = 2

    assert national_metrics.pending_transfer_count == expected_pending_transfer_count


def test_returns_pending_transfer_count_given_a_mixture_of_transfers():
    transfers = [a_pending_transfer(), a_failed_transfer(), an_integrated_transfer()]

    national_metrics = calculate_national_metrics(transfers)

    expected_pending_transfer_count = 1

    assert national_metrics.pending_transfer_count == expected_pending_transfer_count


def test_returns_pending_transfer_count_given_pending_and_pending_with_error_transfers():
    transfers = [a_pending_transfer(), a_pending_with_error_transfer()]

    national_metrics = calculate_national_metrics(transfers)

    expected_pending_transfer_count = 2

    assert national_metrics.pending_transfer_count == expected_pending_transfer_count
