import json
from typing import List

import requests

from gp2gp.odsportal.models import PracticeDetails

ODS_PORTAL_SEARCH_URL = "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations"
DEFAULT_SEARCH_PARAMS = {
    "PrimaryRoleId": "RO177",
    "Status": "Active",
    "NonPrimaryRoleId": "RO76",
    "Limit": "1000",
}

NEXT_PAGE_HEADER = "Next-Page"


class OdsPortalException(Exception):
    def __init__(self, message, status_code):
        super(OdsPortalException, self).__init__(message)
        self.status_code = status_code


class OdsPracticeDataFetcher:
    def __init__(self, client=requests, search_url=ODS_PORTAL_SEARCH_URL):
        self._search_url = search_url
        self._client = client

    def fetch_practice_data(self, params=None):
        if params is None:
            params = DEFAULT_SEARCH_PARAMS
        response_data = list(self._iterate_practice_data(params))
        return response_data

    def _iterate_practice_data(self, params):
        response = self._client.get(self._search_url, params)
        yield from self._process_practice_data_response(response)
        while NEXT_PAGE_HEADER in response.headers:
            response = self._client.get(response.headers[NEXT_PAGE_HEADER])
            yield from self._process_practice_data_response(response)

    @classmethod
    def _process_practice_data_response(cls, response):
        if response.status_code != 200:
            raise OdsPortalException("Unable to fetch practice data", response.status_code)
        return json.loads(response.content)["Organisations"]


def construct_practice_list(data_fetcher=None) -> List[PracticeDetails]:
    if data_fetcher is None:
        data_fetcher = OdsPracticeDataFetcher()
    response = data_fetcher.fetch_practice_data()
    return [PracticeDetails(ods_code=p["OrgId"], name=p["Name"]) for p in response]