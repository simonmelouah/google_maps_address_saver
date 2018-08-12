"""Test for shopify install app."""
from django.test import TestCase, override_settings
from django.conf import settings
from mock import patch, Mock
import json


class BaseClass(object):
    """Base class for setup/teardown."""

    def setUp(self):
        """Setup for tests."""
        self.redirect_url = "https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=82627723617-3eb2532s24313rifep74fbsu25h95mhs.apps.googleusercontent.com&redirect_uri=http://localhost:8000/install/connect&scope=https://www.googleapis.com/auth/fusiontables&state=gK6f4YaBxLaErFxfJfrBFRulFC1JO3&access_type=offline&include_granted_scopes=true"
        self.access_token = "ya29.Glv1BatskWxdiU3U7JJw8AmCJCWNDeQpKl60egb_Rtc3Q9RZu1Of-xf0bMRDRh9R7BxZLD_T82gS5XBdsVUJ_PSkgJ3yR9W-pHx8ipf3DJF8mVXkI5CW6lpgiB00"
        self.refresh_token = "1/wR_RVjvnGaoYcSJVyYGauQC-tJ3ETmh-zU1mU8PRLT_WpUnxAhDxDiSAXl4FqwAH"


class TestGoogleInstall(BaseClass, TestCase):
    """Test class for google_install function."""

    def test_google_install(self):
        """Test to hit the install endpoint."""
        response = self.client.get('/install', follow=True)
        self.assertRedirects(response,
                             expected_url=self.redirect_url,
                             status_code=301,
                             target_status_code=400)


class TestGoogleConnectApp(BaseClass, TestCase):
    """Test class for google_connect_app app."""

    def test_google_connect_app_without_code(self):
        """Confirm if redirect happens when query string code is omitted."""
        response = self.client.get('/install/connect', follow=True)
        self.assertRedirects(response,
                             expected_url=self.redirect_url,
                             status_code=301,
                             target_status_code=400)

    def test_google_connect_app_successful_request_without_refresh_token(self):
        """Confirm if redirect happens to /maps/main/ without refresh token."""
        session = self.client.session
        session["refresh_token"] = self.refresh_token
        session["access_token"] = self.access_token
        session.save()
        response = self.client.get(
            '/install/connect?code=sedwe4rwe', follow=True)
        self.assertRedirects(response,
                             expected_url='/maps/main/',
                             status_code=301,
                             target_status_code=200)

    def test_google_connect_app_successful_request_with_refresh_token(self):
        """Confirm if redirect happens to /maps/main/ with refresh token."""
        with patch('google_install.views.requests.post') as mock_post:
            post_text = str({"refresh_token": self.refresh_token,
                             "access_token": self.access_token})
            mock_post.return_value = Mock(status_code=200, text=post_text)
            response = self.client.get(
                '/install/connect?code=sedwe4rwe', follow=True)
            self.assertRedirects(response,
                                 expected_url='/maps/main/',
                                 status_code=301,
                                 target_status_code=200)
