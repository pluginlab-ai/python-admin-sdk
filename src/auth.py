from typing import Optional, Generic, TypeVar
from dataclasses import dataclass
import json
from token_verifier import TokenVerifier
import requests

@dataclass
class MemberAuth:
    is_verified: bool;
    email: str;
    has_password: bool;
    sign_in_method: str;

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

    
