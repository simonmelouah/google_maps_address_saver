from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.http import require_http_methods
import datetime
import json
import requests
from .models import FusionTable, Address


@require_http_methods(["GET", "POST"])
def maps_main_home(request):
    """Main home page that renders the map."""
    if request.method == "GET":
        return render(request, 'maps_main.html')
    address_json = json.loads(request.body)
    lat = address_json.get('geometry')['location']['lat']
    lng = address_json.get('geometry')['location']['lng']
    formatted_address = address_json.get('formatted_address')
    insert_sql = f"INSERT INTO {request.session.get('fusion_table_id')} (address, coordinates, created_at) VALUES ('{formatted_address}', '{lat} {lng}', '{datetime.datetime.now()}');"
    store_address = requests.post(
        url=f"https://www.googleapis.com/fusiontables/v2/query?sql={insert_sql}",
        headers={
            "Authorization": f"Bearer {request.session.get('access_token')}",
            "Content-Type": "application/json"})
    if store_address.status_code != 200:
        return HttpResponse(status=store_address.status_code)
    fusion_table_object = FusionTable.objects.filter(google_id=request.session.get('fusion_table_id')).first()
    if not fusion_table_object:
        return HttpResponse(status=500)
    Address(
        fusion_table=fusion_table_object,
        latitude=lat,
        longitude=lng,
        full_address=formatted_address
    ).save()
    return HttpResponse(status=200)
