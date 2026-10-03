from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("inscription/", views.signup, name="signup"),
    path("mon-espace/", views.dashboard, name="dashboard"),
    path("shein/", views.shein_new, name="shein_new"),
    path("groupages/", views.groupages, name="groupages"),
    path("groupages/<int:pk>/rejoindre/", views.groupage_join, name="groupage_join"),
    path("tableau-de-bord/", views.admin_dashboard, name="admin_dashboard"),
    path("formations/", views.formations, name="formations"),
    path("formations/<slug:slug>/", views.formation_detail, name="formation_detail"),
]
