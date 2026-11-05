from django.urls import path

from sustentabilidad import views

urlpatterns = [
    path("panel/", views.vista_panel_sustentabilidad, name="panel_sustentabilidad"),
]
