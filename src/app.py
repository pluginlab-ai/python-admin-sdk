import requests
from typing import TypedDict, Optional
from auth import PluginlabAuth
from dataclasses import dataclass

class PluginlabAppConfig(TypedDict):
    secret_key: str
    plugin_id: str
    auth_cert_url: Optional[str]
    auth_url: Optional[str]

@dataclass
class PluginlabApp:
    def __init__(
            self,
            secret_key: str,
            plugin_id: str,
            auth_url = "https://auth.pluginlab.ai/admin/v1/cert",
            auth_cert_url = "https://auth.pluginlab.ai/admin/v1/cert"
        ):
        self.plugin_id = plugin_id
        self.secret_key = secret_key
        self.auth_url = auth_url
        self.auth_cert_url = auth_cert_url

        s = requests.Session()
        s.headers.update()
        self.client = s

    def get_auth(self):
        auth = PluginlabAuth(
                plugin_id=self.plugin_id,
                secret_key=self.secret_key,
                auth_url=self.auth_url,
                auth_cert_url=self.auth_cert_url,
                )

        return auth

    def verify_token(self):
        return ""
