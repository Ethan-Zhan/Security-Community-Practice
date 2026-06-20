import json

from django.test import TestCase

from bind.models import BindInfo
from feishu_auth.models import UserInfo
from utils.token import bind_get_user_info, bind_token_generate


def create_user(open_id, name):
    return UserInfo.objects.create(
        open_id=open_id,
        name=name,
        en_name=name,
        avatar_big="https://example.com/avatar-big.png",
        avatar_middle="https://example.com/avatar-middle.png",
        avatar_thumb="https://example.com/avatar-thumb.png",
        avatar_url="https://example.com/avatar.png",
        tenant_key="tenant",
        union_id=f"union-{open_id}",
    )


class BindSecurityTests(TestCase):
    def setUp(self):
        self.alice = create_user("alice-open-id", "alice")
        self.bob = create_user("bob-open-id", "bob")
        self.client.force_login(self.alice)

    def test_bind_token_is_issued_for_authenticated_user(self):
        response = self.client.post(
            "/bind",
            data=json.dumps({"open_id": self.bob.open_id}),
            content_type="application/json",
            REMOTE_ADDR="10.0.0.10",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        token_info = bind_get_user_info(payload["token"])
        self.assertEqual(token_info["open_id"], self.alice.open_id)
        self.assertEqual(token_info["ip"], "10.0.0.10")

    def test_verify_rejects_token_for_another_authenticated_user(self):
        bob_token = bind_token_generate(BindInfo(user=self.bob, ip="127.0.0.1", device_id=1))

        response = self.client.post(
            "/verify",
            data=json.dumps({"token": bob_token}),
            content_type="application/json",
            REMOTE_ADDR="127.0.0.1",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(BindInfo.objects.count(), 0)
