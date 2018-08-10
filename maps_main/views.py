from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
import requests

@require_http_methods(["GET", "POST"])
def maps_main_home(request):
    """Main home page that renders the map."""
    if request.method == "GET":
        return render(request, 'maps_main.html')
    address_component = json.loads(request.body)
    lat = address_component.get('geometry')['location']['lat']
    lng = address_component.get('geometry')['location']['lng']
    insert_sql = f"INSERT INTO {request.session.get('fusion_table_id')} (address) VALUES ('{lat} {lng}');"
    print(insert_sql)
    all_data = requests.post(url=f"https://www.googleapis.com/fusiontables/v2/query?sql={insert_sql}",
                             headers={
                                "Authorization": f"Bearer {request.session.get('access_token')}",
                                "Content-Type": "application/json"})
    print(all_data.text)
    return HttpResponse(status=200)
