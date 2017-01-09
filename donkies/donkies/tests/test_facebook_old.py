import pytest
from web.models import User
from .import base


class TestFacebook(base.Mixin):
    """
    First part of auth via facebook implemented with
    python social auth library (pso).
    On final pipeline get response from facebook and implement own logic.

    1) Frontend poin browser to /login/facebook/
    2) pso sends browser to facebook site.
    3) User click button login.
    4) pso process all data.
    5) On final pipeline custom implementation.

    If user does not exist - create user (lookup by id).
    Update json field with response.

    Facebook response should have id and email.
    If error - redirect browser to FACEBOOK_FAIL_URL with "message"
    If success - redirect browser to FACEBOOK_SUCCESS_URL with "token"

    """
    def get_pso_dic(self):
        """
        Example from real response from facebook.
        """
        return {
            'link': 'xxx',
            'verified': True,
            'picture': {
                'data': {
                    'url': 'https://scontent.xx.fbcdn.net/v/xxx',
                    'is_silhouette': True
                }
            },
            'access_token': 'xxx',
            'updated_time': '2016-09-07T09:03:36+0000',
            'first_name': 'Bob',
            'timezone': 3,
            'email': 'bob@gmail.com',
            'name': 'Bob Smith',
            'last_name': 'Smith',
            'locale': 'ru_RU',
            'id': '222448744834113',
            'gender': 'male',
            'age_range': {'min': 21}
        }

    @pytest.mark.django_db
    def test_01(self, client):
        """
        Try response without id and email.
        Should get message.
        """
        d = self.get_pso_dic()
        d.pop('id')
        result = User.objects.login_facebook(d)
        assert 'message' in result

        d.pop('email')
        result = User.objects.login_facebook(d)
        assert 'message' in result

    @pytest.mark.django_db
    def test_02(self, client):
        d = self.get_pso_dic()
        result = User.objects.login_facebook(d)
        assert 'token' in result

        user = User.objects.get(fb_id=d['id'])
        assert user.fb_response is not None

        # Try to login again with existing user.
        result = User.objects.login_facebook(d)
        assert 'token' in result
