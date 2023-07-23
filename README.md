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
cursor = paginated_result1.next_page_cursor;

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
    sig = request.headers.get(WebhookHeaders.Signature)
    raw_body = request.get_data(as_text=True)

    if not sig:
        return jsonify({'message': 'No signature was found.'})

    if not webhook.is_signature_valid(raw_body, sig):
        return jsonify({'message': 'Invalid signature.'})

    // process the payload as you like
```
Make sure you are providing the `is_signature_valid` method with the raw body of the request, as it was originally sent.
