from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("dashboard/", views.dashBoard, name="dashboard"),
    path("iiqa/", views.iiqa, name="iiqa"),
    path("ssr/txtverify", views.ssrTextVerify, name="ssrtxtverify"),
    path("ssr/geo", views.ssrGeo, name="ssrgeo"),

    # path("user/<str:pk>", views.user, name="user"),
]
