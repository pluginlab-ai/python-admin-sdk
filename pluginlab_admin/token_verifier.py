from os import name
from typing import Optional
import jwt
from jwt import PyJWKClient
from dataclasses import dataclass

@dataclass
class TokenPayloadUser:
    id: str
    email: str
    name: Optional[str] = None
    given_name: Optional[str] = None
    plan_id: Optional[str] = None
    price_id: Optional[str] = None

@dataclass
class TokenPayload:
    uid: str
    iss: str
    aud: str
    iat: int
    exp: int
    user: TokenPayloadUser

class TokenVerifier:
    def __init__(self, remote_key_url: str, audience: str) -> None:
        self.remote_key_url = remote_key_url
        self.audience = audience

    def _transform_token_payload(self, payload: dict) -> TokenPayload:
        u = payload["user"]
        user = TokenPayloadUser(
            id=u["id"],
            email=u["email"],
            name=u.get("name"),
            given_name=u.get("givenName"),
            plan_id=u.get("planId"),
            price_id=u.get("priceId"),
        )

        return TokenPayload(
            uid=payload["uid"],
            iss=payload["iss"],
            aud=payload["aud"],
            iat=payload["iat"],
            exp=payload["exp"],
            user=user,
        )

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
        payload = self._transform_token_payload(data)

        return payload

