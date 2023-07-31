import requests
from typing import Any, Optional
from dataclasses import dataclass

@dataclass
class EventLocation:
    country_code: str
    subdivision_code: Optional[str] = None

class AppEvent:
    def __init__(self, plugin_id: str, secret_key: str, event_url: str): 
        self.plugin_id = plugin_id
        self.secret_key = secret_key
        self.event_url = event_url

        s = requests.Session()
        s.headers.update({
            'X-PluginLab-Admin-Sdk-Secret': self.secret_key,
            'X-PluginLab-Plugin-Id': self.plugin_id
        })
        self.client = s

    def _make_api_url(self, path: str):
        return f"{self.event_url}{path}"

    def create_custom(
            self,
            event_source: str,
            member_id: Optional[str] = None,
            is_in_quota: Optional[bool] = None,
            location: Optional[EventLocation] = None,
            ) -> None:
        payload: dict[str, Any] = {
                "eventSource": event_source,
        }

        if member_id is not None:
            payload['memberId'] = member_id

        if location is not None:
            payload['location'] = {
                    "subdivisionCode": location.subdivision_code,
                    "countryCode": location.country_code
            }

        if is_in_quota is not None:
            payload['isInQuota'] = is_in_quota

        r = self.client.post(
                self._make_api_url('/events/create-custom'),
                json=payload
            )

        if not r.ok:
            raise ValueError(r.json())


