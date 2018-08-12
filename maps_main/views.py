from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.http import require_http_methods
import datetime
import json
import requests
from .models import FusionTable, Address
from google_install.views import check_access_token


# Check if the access token and refresh token sessions are valid
@check_access_token
@require_http_methods(["GET", "POST", "DELETE"])
def maps_main_home(request):
    """Main home page that renders the map."""
    if request.method == "GET":
        # Get all the addresses associated with the given fusion table
        address_object = Address.objects.filter(
            fusion_table__google_id=request.session.get("fusion_table_id")).all()
        # Create a sql query to send to google fusion tables to get the addresses
        sql = f"SELECT * FROM {request.session.get('fusion_table_id')}"
        fusion_table_response = requests.get(
            url=f"https://www.googleapis.com/fusiontables/v2/query?sql={sql}",
            headers={
                "Authorization": f"Bearer {request.session.get('access_token')}",
                "Content-Type": "application/json"})
        # If the request is successful, convert it to JSON and render the map
        # containing all the markers
        if fusion_table_response.status_code != 200:
            return HttpResponse(status=fusion_table_response.status_code)
        fusion_table_values = json.loads(fusion_table_response.text)
        return render(
            request,
            'maps_main.html',
            {
                'fusion_table_rows': fusion_table_values.get("rows"),
                'address_data': address_object,
                'map_centre_lat': fusion_table_values.get("rows")[0][1] if fusion_table_values.get("rows") else None,
                'map_centre_lng': fusion_table_values.get("rows")[0][2] if fusion_table_values.get("rows") else None})
    elif request.method == "POST":
        # If a post request is sent (from the user clicking a valid location
        # on the map), convert the request body to json and get
        # the lat and lng coordinates and formatted_address sent by the click
        address_json = json.loads(request.body)
        lat = address_json.get('geometry')['location']['lat']
        lng = address_json.get('geometry')['location']['lng']
        formatted_address = address_json.get('formatted_address')
        address_object = Address.objects.filter(
            full_address=formatted_address).first()
        # Check if the address already exists, if it does, do nothing,
        # otherwise create a new address
        if not address_object:
            # Generate the INSERT query using the fusin table id session
            insert_sql = f"INSERT INTO {request.session.get('fusion_table_id')} (address, lat, lng, created_at) VALUES ('{formatted_address}', {lat}, {lng}, '{datetime.datetime.now()}');"
            store_address = requests.post(
                url=f"https://www.googleapis.com/fusiontables/v2/query?sql={insert_sql}",
                headers={
                    "Authorization": f"Bearer {request.session.get('access_token')}",
                    "Content-Type": "application/json"})
            # Ensure successful request
            if store_address.status_code != 200:
                return HttpResponse(status=store_address.status_code)
            # Save the address and its fusion table reference to the database
            fusion_table_object = FusionTable.objects.filter(
                google_id=request.session.get('fusion_table_id')).first()
            if not fusion_table_object:
                return HttpResponse(status=500)
            Address(
                fusion_table=fusion_table_object,
                latitude=lat,
                longitude=lng,
                full_address=formatted_address
            ).save()
        return HttpResponse(status=200)
    elif request.method == "DELETE":
        # If a delete request comes in, generate the delete sql query for the
        # fusion table - if the delete request to the google fusion table api
        # is successful, then delete all associated addresses from the database
        delete_sql = f"DELETE FROM {request.session.get('fusion_table_id')};"
        delete_addresses = requests.post(
            url=f"https://www.googleapis.com/fusiontables/v2/query?sql={delete_sql}",
            headers={
                "Authorization": f"Bearer {request.session.get('access_token')}",
                "Content-Type": "application/json"})
        if delete_addresses.status_code == 200:
            Address.objects.filter(
                fusion_table__google_id=request.session.get('fusion_table_id')).delete()
            return HttpResponse(status=200)
        return HttpResponse(status=delete_addresses.status_code)
