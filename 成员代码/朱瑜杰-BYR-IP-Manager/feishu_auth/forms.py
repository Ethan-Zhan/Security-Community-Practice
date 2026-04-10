from django import forms

from .models import User, UserInfo


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = (
            "name",
            "en_name",
            "avatar_big",
            "avatar_middle",
            "avatar_thumb",
            "avatar_url",
            "open_id",
            "tenant_key",
            "union_id",
        )
