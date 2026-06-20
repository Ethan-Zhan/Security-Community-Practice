import json

from django.test import TestCase

from bind.models import BindInfo
from feishu_auth.models import UserInfo


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


class DeviceAuthorizationTests(TestCase):
    def setUp(self):
        self.alice = create_user("alice-open-id", "alice")
        self.bob = create_user("bob-open-id", "bob")
        self.bob_device = BindInfo.objects.create(user=self.bob, ip="10.0.0.2", device_id=1)
        self.client.force_login(self.alice)

    def test_devices_list_ignores_spoofed_open_id(self):
        response = self.client.generic(
            "GET",
            "/devices",
            data=json.dumps({"open_id": self.bob.open_id}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["devices"], [])

    def test_unbound_cannot_delete_another_users_device(self):
        response = self.client.delete(
            f"/devices/{self.bob_device.device_id}",
            data=json.dumps({"open_id": self.bob.open_id}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(BindInfo.objects.filter(pk=self.bob_device.pk).exists())
