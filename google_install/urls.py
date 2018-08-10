from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.install_google_app,
        name='install_google_app'),
    url(r'^connect/$', views.connect_google_app,
        name='connect_google_app'),
    url(r'^create-fusion-table/$', views.create_fusion_table,
        name='create_fusion_table'),
        ]
