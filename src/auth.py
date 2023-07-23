from token_verifier import TokenVerifier
from dataclasses import dataclass

@dataclass
class PluginlabAuth:
    def __init__(self, plugin_id: str, secret_key: str, auth_url: str, auth_cert_url: str): 
        self.plugin_id = plugin_id
        self.secret_key = secret_key
        self.auth_url = auth_url
        self.auth_cert_url = auth_cert_url

        audience = f"plugin:{self.plugin_id}:admin"
        self.token_verifier = TokenVerifier(
                remote_key_url=self.auth_cert_url,
                audience=audience
            )

    def verify_token(self, token: str):
        return self.token_verifier.verify_token(token)
