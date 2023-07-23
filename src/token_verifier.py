import jwt
from jwt import PyJWKClient

class TokenVerifier:
    def __init__(self, remote_key_url: str, audience: str) -> None:
        self.remote_key_url = remote_key_url
        self.audience = audience

    def verify_token(self, token: str):
        jwks_client = PyJWKClient(self.remote_key_url)
        signing_keys = jwks_client.get_signing_keys(refresh=False)
        key = signing_keys[0].key

        data = jwt.decode(
            token,
            key,
            algorithms=["PS256"],
            audience=self.audience,
            options={"verify_exp": True},
        )

        return data

