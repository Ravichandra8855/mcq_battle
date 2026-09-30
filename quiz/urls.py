from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("create/", views.create_room, name="create_room"),
    path("join/", views.join_room, name="join_room"),
    path("battle/<str:code>/", views.battle, name="battle"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    # REST API
    path("api/questions/", views.QuestionListView.as_view()),
    path("api/leaderboard/", views.LeaderboardView.as_view()),
    path("api/matches/", views.MyMatchesView.as_view()),
]
