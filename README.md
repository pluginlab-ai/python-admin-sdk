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
auth = app.get_auth()

# usually you'd get the token from the Authorization header of the HTTP request, formatted as `Bearer <token>`
token = "eyJhbGc...dQssw5c"

try:
    payload = auth.verify_token(token)
    # from that point we know the information in the token hasn't been tampered with

    # we could, for instance, check if the user has a given plan and take specific action based on that
    premium_plan_id = 'KWsmKyJnHBF2Dz1mETDF'
    plan_id = payload.user.plan_id

    if plan_id:
        if plan_id == premium_plan_id: 
            do_something_special()
        else
            do_other_stuff()

    print(payload.uid)
except Exception as e:
    print(f"An error occurred while verifying the token: {e}")
```

The verified token payload is represented by the following typings:

```python
class TokenPayloadUser:
    id: str
    email: str
    name: Optional[str] = None
    given_name: Optional[str] = None
    plan_id: Optional[str] = None
    price_id: Optional[str] = None

class TokenPayload:
    uid: str
    iss: str
    aud: str
    iat: int
    exp: int
    user: TokenPayloadUser
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

### Get member identities

Once a user logs in to your PluginLab portal using a third-party authentication provider, they get assigned an identity for that specific provider.
An identity might contain what you need to interact with the service on behalf of your user such as an access token or a refresh token.
To retrieve all the identities for a given user, use the `auth.get_member_identities` method:

```python
identities = auth.get_member_identities("mem_66c72702dfd9c9a34e80cae434a4bf7e6d3d37df")

if identities.google is not None:
    print("Google identity found, access token is ", identities.google.access_token)

if identities.github is not None:
    # do your stuff

# This applies to every third-party auth provider supported by PluginLab although each might give or not give some information.
```

Here is the class used to represent an identity:

```python
@dataclass
class IdentityProviderData:
    provider: str;
    provider_user_id: str;
    access_token_expires_at_ms: int | None;
    refresh_token_expires_at_ms: int | None;
    last_used_at_ms: int | None;
    access_token: str | None;
    refresh_token: str | None;
```

## List members

### Basic

```python
paginated_result = auth.get_members()

for member in paginated_result.items:
    print(member.id)
```

### With adjustable limit and pagination

You can request up to 100 members at a time and get a specific page by providing a cursor obtained from a previous call.

```python
paginated_result1 = auth.get_members(50)
cursor = paginated_result1.next_page_cursor

if not cursor is None:
    paginated_result2 = auth.get_members(50, cursor)
```

## Create a member

```python
created_member = auth.create_member(
        email='johndoe@example.com',
        password='12345',
        is_verified=True,
        metadata={
            'origin': 'backend-sdk'
        }
)

print(created_member)
```

As the typings show, both `is_verified` and `metadata` fields are optional to create a user.

## Update a member

```python
auth.update_member(
        id='mem_ec9fd884f7fc81fc9e5576d213b6e826d3109d26',
        given_name="John the king of examples",
        family_name="Doe",
        name="John Doe",
        picture_url="https://example.com/john-doe.png",
        metadata={}
)
```

Except the `id` field that is used to identify the user to update, all the other updatable fields are optional in this function call.

## Delete a member

```python
auth.delete_member(
    id='mem_ec9fd884f7fc81fc9e5576d213b6e826d3109d26',
)
```
Note that the member ID is derived from the email the user used to sign up. Therefore recreating an account with the same email will NOT reset usage quotas.

## Dealing with webhooks

Pluginlab signs each webhook payload it sends you using a secret key you can retrieve from your [webhooks settings on the Pluginlab dashboard](https://app.pluginlab.ai/plugin/webhooks).

This package provides facilities to easiliy verifiy the payload of a webhook.

Here is how, using a flask handler as an example:

```typescript
import os
from pluginlab_admin import WebhookHeaders, Webhook

webhook_secret = os.getenv('WEBHOOK_SECRET')
webhook = Webhook(webhook_secret)

@app.route('/webhook', methods=['POST'])
def api():
    sig = request.headers.get(WebhookHeaders.Signature.value)
    raw_body = request.get_data(as_text=True)

    if not sig:
        return jsonify({'message': 'No signature was found.'})

    if not webhook.is_signature_valid(raw_body, sig):
        return jsonify({'message': 'Invalid signature.'})

    // process the payload as you like
```
Make sure you are providing the `is_signature_valid` method with the raw body of the request, as it was originally sent.

## Events

On PluginLab, an event is used as a representaiton of a plugin request and is traditionally generated on each request made by ChatGPT.
The SDK offers limited but useful utilities to deal with events.

To get started, you need to leverage the event service by calling the `app.get_event` method.

```typescript
// assuming app was previously initialized as showed above
event = app.get_event();
```

### Create a custom event

If you want to create custom events that will appear in your PluginLab dashboard and count as part of your users' quota, you can rely on the `create_custom` method.


This is especially useful if your service is accessible from other means that ChatGPT but you still want to account for usage using PluginLab.


```python
from pluginlab_admin import EventLocation

location = EventLocation(
    country_code="US",
    subdivision_code="CA", # optional
)

event.create_custom(
    # case insensitive, max. 10 chars
    event_source="WEB_UI",
    # optional, quota ignored if not present
    member_id="mem_fd9a1ba5e385e3d97412cdfbd7b8284c4f0c8e18",
    # optional
    location=location,
    # optional, defaults to true
    is_in_quota=True
)
```

Assuming the provided `member_id` refers to a valid plugin member then a new event will get created once the above code runs. It will appear in your PluginLab dashboard's event section.
