import requests

from .event import AppEvent
from .auth import AppAuth

class App:
    def __init__(
            self,
            secret_key: str,
            plugin_id: str,
            auth_url = "https://auth.pluginlab.ai",
            auth_cert_url = "https://auth.pluginlab.ai/admin/v1/cert",
            event_url = "https://event.pluginlab.ai"
        ):
        self.plugin_id = plugin_id
        self.secret_key = secret_key
        self.auth_url = auth_url
        self.auth_cert_url = auth_cert_url
        self.event_url = event_url

        s = requests.Session()
        s.headers.update({
            'X-PluginLab-Admin-Secret': self.secret_key,
            'X-PluginLab-Plugin-Id': self.plugin_id
        })
        self.client = s

    def get_auth(self):
        auth = AppAuth(
                plugin_id=self.plugin_id,
                secret_key=self.secret_key,
                auth_url=self.auth_url,
                auth_cert_url=self.auth_cert_url,
                )

        return auth

    def get_event(self) -> AppEvent:
        event = AppEvent(
                plugin_id=self.plugin_id,
                secret_key=self.secret_key,
                event_url=self.event_url,
        )

        return event
        
