import hashlib
import hmac
from enum import Enum

class WebhookHeaders(Enum):
    Signature = 'X-PluginLab-Signature'
    Event = 'X-PluginLab-Event'
    DeliveryId = 'X-PluginLab-Delivery-Id'
    HookId = 'X-PluginLab-Hook-Id'
    PluginId = 'X-PluginLab-Plugin-Id'
    SignatureVersion = 'X-PluginLab-Signature-Version'
    SignatureAlgorithm = 'X-PluginLab-Signature-Algorithm'
    PoweredBy = 'X-Powered-By'
    Timestamp = 'X-PluginLab-Timestamp'

class Webhook:
    def __init__(self, secret: str):
        self.secret = secret;

    def is_signature_valid(self, body: str, sig: str):
        h = hmac.new(self.secret.encode(), body.encode(), hashlib.sha256)
        expected_sig = h.hexdigest()

        return sig == expected_sig

    def verify_signature(self, body: str, sig: str):
        if not self.is_signature_valid(body, sig):
            raise Exception(f"signature mismatch")
