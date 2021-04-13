from typing import List

from prmdata.domain.ods_portal.models import PracticeDetails


class PracticeLookup:
    def __init__(self, practices: List[PracticeDetails]):
        self._practices = practices
        self._asid_to_ods_mapping = {
            asid: practice.ods_code for practice in self._practices for asid in practice.asids
        }

    def has_asid_code(self, asid):
        return asid in self._asid_to_ods_mapping

    def ods_code_from_asid(self, asid):
        return self._asid_to_ods_mapping.get(asid)

    def all_practices(self):
        return iter(self._practices)