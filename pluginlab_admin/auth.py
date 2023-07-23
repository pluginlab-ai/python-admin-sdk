from typing import Any, Optional, Generic, TypeVar
from dataclasses import dataclass
from enum import Enum
import json
from .token_verifier import TokenVerifier
import requests

class SignInMethodId(Enum):
    EMAIL_AND_PASSWORD = 'email-and-password'
    MAGIC_EMAIL_CODE = 'magic-email-code'
    GOOGLE = 'google'

@dataclass
class MemberAuth:
    is_verified: bool;
    email: str;
    has_password: bool;
    sign_in_method: SignInMethodId;

@dataclass
class Member:
    id: str;
    auth: MemberAuth;
    name: Optional[str]
    given_name: Optional[str]
    family_name: Optional[str]
    picture_url: Optional[str]
    custom_fields: dict[str, str];
    metadata: dict[str, str];
    created_at_ms: int;
    updated_at_ms: int;

T = TypeVar('T')

@dataclass
class PaginatedResponse(Generic[T]):
    items: list[T]
    total: int
    next_page_cursor: Optional[str]

class AppAuth:
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
        s = requests.Session()
        s.headers.update({
            'X-PluginLab-Admin-Sdk-Secret': self.secret_key,
            'X-PluginLab-Plugin-Id': self.plugin_id
        })
        self.client = s

    def _make_api_url(self, path: str):
        return f'{self.auth_url}/admin/plugins/{self.plugin_id}{path}'

    def _transform_raw_member(self, json: dict) -> Member:
        auth = json['auth']
        member_auth = MemberAuth(
            is_verified=auth['isVerified'],
            email=auth['email'],
            has_password=auth['hasPassword'],
            sign_in_method=auth['signInMethod']
        )

        return Member(
            id=json['id'],
            auth=member_auth,
            name=json.get('name', None),
            given_name=json.get('givenName', None),
            family_name=json.get('familyName', None),
            picture_url=json.get('pictureUrl', None),
            custom_fields=json['customFields'],
            metadata=json['metadata'],
            created_at_ms=json['createdAtMs'],
            updated_at_ms=json['updatedAtMs']
        )
        
    def verify_token(self, token: str):
        return self.token_verifier.verify_token(token)

    def get_member_by_email(self, email: str) -> Optional[Member]:
        url = self._make_api_url(f'/member/byEmail/{email}')
        res = self.client.get(url)

        if res.status_code == 404:
            return None

        if res.status_code != 200:
            error_data = str(res.content)
            raise Exception(f'An unknown error occured: {error_data}')

        raw_member = json.loads(res.content)
        member = self._transform_raw_member(raw_member)

        return member

    def get_member_by_id(self, id: str) -> Optional[Member]:
        url = self._make_api_url(f'/members/{id}')
        res = self.client.get(url)

        if res.status_code == 404:
            return None

        if res.status_code != 200:
            error_data = str(res.content)
            raise Exception(f'An unknown error occured: {error_data}')

        raw_member = json.loads(res.content)
        member = self._transform_raw_member(raw_member)

        return member

    def get_members(self, limit = 50, start_after: Optional[str] = None) -> PaginatedResponse[Member]:
        url = self._make_api_url(f'/members?limit={limit}&startAfter={start_after}')
        res = self.client.get(url)

        if res.status_code != 200:
            error_data = str(res.content)
            raise Exception(f'An unknown error occured: {error_data}')

        j = json.loads(res.content)

        raw_members = j['items']
        members = [self._transform_raw_member(m) for m in raw_members]
        paginated_res = PaginatedResponse[Member](
            items=members,
            total=j['total'],
            next_page_cursor=j['nextPageToken']
        )

        return paginated_res

    def create_member(self, email: str, password: str, is_verified: Optional[bool] = None, metadata: Optional[dict[str, str]] = None):
        url = self._make_api_url('/members')
        data: dict[str, Any] = {
            'email': email,
            'password': password,
        }

        if is_verified is not None:
            data['isVerified'] = is_verified
        if metadata is not None:
            data['metadata'] = metadata

        res = self.client.post(url, json=data)

        if res.status_code != 201:
            error_data = str(res.content)
            raise Exception(f'An unknown error occured: {error_data}')

        raw_member = json.loads(res.content)
        member = self._transform_raw_member(raw_member)

        return member

    def update_member(
            self,
            id: str,
            name: Optional[str] = None,
            given_name: Optional[str] = None,
            family_name: Optional[str] = None,
            picture_url: Optional[str] = None,
            metadata: Optional[dict[str, str]] = None,
            ) -> Member:
        url = self._make_api_url(f'/members/{id}')
        data: dict[str, Any] = {}

        if name is not None:
            data['name'] = name
        if given_name is not None:
            data['givenName'] = given_name
        if family_name is not None:
            data['familyName'] = family_name
        if picture_url is not None:
            data['pictureUrl'] = picture_url
        if metadata is not None:
            data['metadata'] = metadata

        res = self.client.patch(url, json=data)

        if not res.ok:
            error_data = str(res.content)
            raise Exception(f'An error occured: {error_data}')

        raw_member = json.loads(res.content)
        member = self._transform_raw_member(raw_member)

        return member


    def delete_member(self, id: str) -> None:
        url = self._make_api_url(f'/members/{id}')
        res = self.client.delete(url)

        if not res.ok:
            error_data = str(res.content)
            raise Exception(f'An unknown error occured: {error_data}')
