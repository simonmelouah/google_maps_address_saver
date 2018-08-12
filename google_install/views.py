from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
# import google_auth_oauthlib
from google_maps_address_saver import settings
import requests
import json
from .models import GoogleUser
from maps_main.models import FusionTable
from functools import wraps

def check_access_token(input_function):
    def wrap(request, *args, **kwargs):
        if not request.session.get('refresh_token') and not request.session.get('access_token'):
            return redirect('/install')
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "refresh_token": request.session.get('refresh_token'),
            "grant_type": "refresh_token"
        }

        resp = requests.post(
            "https://www.googleapis.com/oauth2/v4/token", data=params).json()
        request.session["access_token"] = resp.get("access_token")
        return input_function(request, *args, **kwargs)
    wrap.__doc__=input_function.__doc__
    wrap.__name__=input_function.__name__
    return wrap

def error_handler(request):
    return redirect('/install')


@require_http_methods(["GET"])
def install_google_app(request):
    """Main home page that renders the map."""
    url = f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={settings.GOOGLE_REDIRECT_URI}&scope={settings.GOOGLE_SCOPE}&state=gK6f4YaBxLaErFxfJfrBFRulFC1JO3&access_type=offline&include_granted_scopes=true"
    return redirect(url)


@require_http_methods(["GET"])
def connect_google_app(request):
    """Main home page that renders the map."""
    if not request.GET.get('code'):
        return redirect('/install')
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
        return redirect('/install/create-fusion-table/')
    return redirect('maps_main_home')


@check_access_token
@require_http_methods(["GET"])
def create_fusion_table(request):
    table_params = {
            "columns": [
                {
                    "kind": "fusiontables#column",
                    "columnId": 1,
                    "name": "address",
                    "type": "STRING"
                },
                {
                    "kind": "fusiontables#column",
                    "columnId": 2,
                    "name": "lat",
                    "type": "NUMBER"
                },
                {
                    "kind": "fusiontables#column",
                    "columnId": 3,
                    "name": "lng",
                    "type": "NUMBER"
                },
                {
                    "kind": "fusiontables#column",
                    "columnId": 4,
                    "name": "created_at",
                    "type": "DATETIME"
                }
            ],
            "isExportable": False,
            "name": "Google Maps Address Saver"
        }
    create_table = requests.post(
        url="https://www.googleapis.com/fusiontables/v2/tables",
        data=json.dumps(table_params),
        headers={
            "Authorization": f"Bearer {request.session.get('access_token')}",
            "Content-Type": "application/json"})
    if create_table.status_code != 200:
        return HttpResponse(f"<h2>Error in creating table: {create_table.text}</h2>")
    create_table_json = json.loads(create_table.text)
    google_user_object = GoogleUser.objects.filter(refresh_token=request.session.get('refresh_token')).first()
    FusionTable(
        google_user=google_user_object,
        name="Google Maps Address Saver",
        google_id=create_table_json.get("tableId")
    ).save()
    request.session["fusion_table_id"] = create_table_json.get("tableId")
    return redirect('maps_main_home')
