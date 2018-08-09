from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
# import google_auth_oauthlib
from google_maps_address_saver import settings
import requests
import json
from .models import GoogleUser


@require_http_methods(["GET"])
def install_google_app(request):
    """Main home page that renders the map."""
    url = f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={settings.GOOGLE_REDIRECT_URI}&scope={settings.GOOGLE_SCOPE}&state=gK6f4YaBxLaErFxfJfrBFRulFC1JO3&access_type=offline&include_granted_scopes=true"
    # return HttpResponse(url)
    return redirect(url)


@require_http_methods(["GET"])
def connect_google_app(request):
    """Main home page that renders the map."""
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "code": request.GET.get('code'),
        "grant_type": "authorization_code",
        "redirect_uri": settings.GOOGLE_REDIRECT_URI
    }
    auth_resp = requests.post(
        "https://www.googleapis.com/oauth2/v4/token", data=params).json()
    if auth_resp.get("refresh_token"):
        GoogleUser(
            access_token=auth_resp.get("access_token"),
            refresh_token=auth_resp.get("refresh_token")
        ).save()
        request.session["access_token"] = auth_resp.get("access_token")
        request.session["refresh_token"] = auth_resp.get("refresh_token")
    return HttpResponse("Success!")
