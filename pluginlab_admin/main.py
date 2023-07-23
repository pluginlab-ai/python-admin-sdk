from app import App
from webhook import Webhook

app = App(
    secret_key="e1e167da10cdeb18dd4161c5a03dd2c13e715a648acb9185dcd382271d5eb645",
    plugin_id="9f2eda92911568d124f15e3bab12d3c5",
    auth_cert_url="https://auth-service-id3yozdp5q-uc.a.run.app/admin/v1/cert",
    auth_url="https://auth-service-id3yozdp5q-uc.a.run.app"
)

auth = app.get_auth()

token = auth.verify_token('eyJhbGciOiJQUzI1NiJ9.eyJ1aWQiOiJtZW1fMjY0MGZjMzc1ZmI4MDc3NGJkOWNlNjhjZjE4MDc5MDgxNzk3NWI5ZSIsImF1ZCI6InBsdWdpbjo5ZjJlZGE5MjkxMTU2OGQxMjRmMTVlM2JhYjEyZDNjNTphZG1pbiIsImlzcyI6Imh0dHBzOi8vYXV0aC5wbHVnaW5sYWIuYWkiLCJpYXQiOjE2OTAwNzA0NTMsImV4cCI6MTY5MDI0MzI1M30.b1yYkfzLBm7aaL9gkuQaUg0woUOsNGYjyRge8G_DuuxZ4ZYCVk30UiT_aBETl26Sq13p0godrLvvEFaMv734CHERqQZhKg6WfujSXFUId7eRET7U9hos435ePBV2mBqKzRXq51-574mTZUIme5ZgsU7mUwRlN67FfSIc3zvGrKv6nw542B6tfiqkCVr2qGECtkT0BpPspeNp_V-iBa55Rfn6D1ocWcXjzInlQGgOk-tMuCYmqoh2qwVvvFtUZS1StpZl-YVaie0MR19BXPbwkzUhWaA3O-b-8DpyK0fKPeQIC8nN8gSb0HGBgUOS5tmyDxh9_llHuBLP5hnIc5a-BQ')

print(token)

