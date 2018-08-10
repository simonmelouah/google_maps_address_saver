from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
# import google_auth_oauthlib
from google_maps_address_saver import settings
import requests
import json
from .models import GoogleUser
from maps_main.models import FusionTable


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
        print("Creating Fusion table")
        GoogleUser(
            access_token=auth_resp.get("access_token"),
            refresh_token=auth_resp.get("refresh_token")
        ).save()
        request.session["access_token"] = auth_resp.get("access_token")
        request.session["refresh_token"] = auth_resp.get("refresh_token")
        return redirect('/install/create-fusion-table/')
    return redirect('maps_main_home')


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
                    "columnId": 1,
                    "name": "coordinates",
                    "type": "LOCATION"
                },
                {
                    "kind": "fusiontables#column",
                    "columnId": 2,
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
