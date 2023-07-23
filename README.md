# python-admin-sdk

# Install

```bash
pip install pluginlab_admin
```

# Getting started

Get started by initializing the Pluginlab app:

```python
from pluginlab_admin import App

app = App(
    secret_key="<PLUGIN_SECRET>",
    plugin_id="<PLUGIN_ID>",
)

# to manage auth-related stuff, mostly members
auth = app.get_auth()
```

The SDK secret should be generated [from your Pluginlab dashboard](https://app.pluginlab.ai/plugin/admin-sdk).

## Verify the user token

Everytime ChatGPT will talk to your backend through the PluginLab proxy, it will send the user token in the Authorization header as a bearer token.
You can verify the integrity of such token by using the `verify_token` method:

```python
auth = app.get_auth();

# usually you'd get the token from the Authorization header of the HTTP request, formatted as `Bearer <token>`
token = "eyJhbGc...dQssw5c"

try:
    payload = auth.verify_token(token)
    print(payload.uid)
except Exception as e:
    print(f"An error occurred while verifying the token: {e}")
```

## Get a member by id or email

### By email


```python
member = auth.get_member_by_email('johndoe@example.com')

if member is None:
    print('No such member.')
else
    print(f'Member with email {member.auth.email} signed up with method "{member.auth.sign_in_method}"')
```

### By id


```python
member = auth.get_member_by_id('mem_ec9fd884f7fc81fc9e5576d213b6e826d3109d26')

if member is None:
    print('No such member.')
else
    print(f'Member with id {member.id} (email={member.auth.email}) signed up with method "{member.auth.sign_in_method}"')
```

A member is represented with the following typings:

```python
class SignInMethodId(Enum):
    EMAIL_AND_PASSWORD = 'email-and-password'
    MAGIC_EMAIL_CODE = 'magic-email-code'
    GOOGLE = 'google'

class MemberAuth:
    is_verified: bool;
    email: str;
    has_password: bool;
    sign_in_method: SignInMethodId;

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
```
