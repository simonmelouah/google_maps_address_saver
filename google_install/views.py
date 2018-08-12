from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from google_maps_address_saver import settings
import requests
import json
from .models import GoogleUser
from maps_main.models import FusionTable
from functools import wraps


def check_access_token(input_function):
    """Decorator to check if the user has an access token and if it's valid."""
    def wrap(request, *args, **kwargs):
        """Wrap to check for refresh/access token."""
        # If the user doesn't have a refresh and access token, redirect them
        # to the install endpoint.
        if not request.session.get(
                'refresh_token') and not request.session.get('access_token'):
            return redirect('/install')
        # If the user has a refresh and access token, send an access token
        # refresh request to the google oauth2 endpoint
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
    wrap.__doc__ = input_function.__doc__
    wrap.__name__ = input_function.__name__
    return wrap


@require_http_methods(["GET"])
def install_google_app(request):
    """Base install endpoint, first endpoint to navigate to."""
    # Get the client_id, secret and scope from settings.py
    url = f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={settings.GOOGLE_REDIRECT_URI}&scope={settings.GOOGLE_SCOPE}&state=gK6f4YaBxLaErFxfJfrBFRulFC1JO3&access_type=offline&include_granted_scopes=true"
    return redirect(url)


@require_http_methods(["GET"])
def connect_google_app(request):
    """Main home page that renders the map."""
    # If the url doesn't contain the code query string, redirect them to /install
    if not request.GET.get('code'):
        return redirect('/install')
    # Authenticate the user
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "code": request.GET.get('code'),
        "grant_type": "authorization_code",
        "redirect_uri": settings.GOOGLE_REDIRECT_URI
    }
    auth_resp = requests.post(
        "https://www.googleapis.com/oauth2/v4/token", data=params)
    # If unsuccessful response, return the status code
    if auth_resp.status_code != 200:
        return HttpResponse(status=auth_resp.status_code)
    # Convert the response text into json
    auth_json = json.loads(auth_resp.text)
    # Set the access token and refresh token sessions for later reference
    request.session["access_token"] = auth_json.get("access_token")
    request.session["refresh_token"] = auth_json.get("refresh_token")
    # For already authenticated users, google does not return the refresh_token
    # in the response payload. The below conditional checks if the user
    # is new (i.e. contains the refresh token in the response payload) and
    # if they are redirect to the maps main endpoint otherwise create a new
    # fusion table.
    if auth_json.get("refresh_token"):
        GoogleUser(
            access_token=auth_json.get("access_token"),
            refresh_token=auth_json.get("refresh_token")
        ).save()
        create_fusion_table(request)
    return redirect('maps_main_home')


def create_fusion_table(request):
    """This function creates a new fusion table in google drive."""
    # Send the request to create the new table
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
    # If the request is not successful return an error
    if create_table.status_code != 200:
        return HttpResponse(
            f"<h2>Error in creating table: {create_table.text}</h2>")
    # If the request is successful store the fusion table reference in the
    # database
    create_table_json = json.loads(create_table.text)
    google_user_object = GoogleUser.objects.filter(
        refresh_token=request.session.get('refresh_token')).first()
    FusionTable(
        google_user=google_user_object,
        name="Google Maps Address Saver",
        google_id=create_table_json.get("tableId")
    ).save()
    # Set the fusion table id session to refrence later
    request.session["fusion_table_id"] = create_table_json.get("tableId")
