from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^main/$', views.maps_main_home,
        name='maps_main_home'),
        ]
