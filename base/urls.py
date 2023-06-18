from django.urls import path
from base import views


urlpatterns = [
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("sing-up/", views.register, name="register"),
    path("", views.home, name="home"),
    path("room/<str:pk>/", views.room, name="room"),
    path("topics/", views.topics, name="topics"),
    path("activities/", views.activities, name="activities"),
    path("profile/<str:pk>", views.userProfile, name="user-profile"),
    path("user-settings/", views.userSettings, name="user-settings"),
    path("create-room/", views.createRoom, name="create-room"),
    path("update-room/<str:pk>/", views.updateRoom, name="update-room"),
    path("delete-room/<str:pk>/", views.deleteRoom, name="delete-room"),
    path("delete-message/<str:pk>/", views.deleteMessage, name="delete-message"),
]
