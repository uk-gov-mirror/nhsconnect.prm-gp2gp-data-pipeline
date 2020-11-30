from gp2gp.service.models import Transfer, PracticeSlaMetrics, TransferStatus
from tests.builders.common import a_string, a_duration, an_integer


def build_transfer(**kwargs):
    return Transfer(
        conversation_id=kwargs.get("conversation_id", a_string(36)),
        sla_duration=kwargs.get("sla_duration", a_duration()),
        requesting_practice_ods_code=kwargs.get("requesting_practice_ods_code", a_string(6)),
        sending_practice_ods_code=kwargs.get("sending_practice_ods_code", a_string(6)),
        final_error_code=kwargs.get("final_error_code", None),
        intermediate_error_codes=kwargs.get("intermediate_error_codes", []),
        pending=kwargs.get("pending", False),
        status=kwargs.get("status", TransferStatus.PENDING),
    )


def build_practice_sla_metrics(**kwargs):
    return PracticeSlaMetrics(
        ods_code=kwargs.get("ods_code", a_string(6)),
        name=kwargs.get("name", a_string()),
        within_3_days=kwargs.get("within_3_days", an_integer()),
        within_8_days=kwargs.get("within_8_days", an_integer()),
        beyond_8_days=kwargs.get("beyond_8_days", an_integer()),
    )
