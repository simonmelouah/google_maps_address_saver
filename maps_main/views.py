from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.http import require_http_methods
import datetime
import json
import requests
from .models import FusionTable, Address
from google_install.views import check_access_token


@check_access_token
@require_http_methods(["GET", "POST"])
def maps_main_home(request):
    """Main home page that renders the map."""
    if request.method == "GET":
        sql = f"SELECT * FROM {request.session.get('fusion_table_id')}"
        fusion_table_values = requests.get(
            url=f"https://www.googleapis.com/fusiontables/v2/query?sql={sql}",
            headers={
                "Authorization": f"Bearer {request.session.get('access_token')}",
                "Content-Type": "application/json"}).json()
        return render(request, 'maps_main.html',
                      {'fusion_table_rows': fusion_table_values.get("rows"),
                       'map_centre_lat': fusion_table_values.get("rows")[0][1] if fusion_table_values.get("rows") else None,
                       'map_centre_lng': fusion_table_values.get("rows")[0][2] if fusion_table_values.get("rows") else None})
    address_json = json.loads(request.body)
    lat = address_json.get('geometry')['location']['lat']
    lng = address_json.get('geometry')['location']['lng']
    formatted_address = address_json.get('formatted_address')
    insert_sql = f"INSERT INTO {request.session.get('fusion_table_id')} (address, lat, lng, created_at) VALUES ('{formatted_address}', {lat}, {lng}, '{datetime.datetime.now()}');"
    store_address = requests.post(
        url=f"https://www.googleapis.com/fusiontables/v2/query?sql={insert_sql}",
        headers={
            "Authorization": f"Bearer {request.session.get('access_token')}",
            "Content-Type": "application/json"})
    if store_address.status_code != 200:
        print(request.session.get('access_token'), store_address.text)
        return HttpResponse(status=store_address.status_code)
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
