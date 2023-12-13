from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_search, name="event_search"),
    path('band/<int:band_id>/<int:from_account>/', views.band, name="band"),
    path('account/', views.account, name="account"),
    path('login/', views.login_view, name="login"),
    path('register/', views.register_view, name="register"),
    path('logout', views.logout_view, name="logout")
    ]