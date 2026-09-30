import random
import string

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Match, Question
from .serializers import MatchSerializer, QuestionSerializer


# ---------- Pages ----------
def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.save())
        return redirect("home")
    return render(request, "registration/register.html", {"form": form})


@login_required
def home(request):
    return render(request, "quiz/home.html")


@login_required
def create_room(request):
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return redirect("battle", code=code)


@login_required
def join_room(request):
    code = request.GET.get("code", "").strip().upper()
    return redirect("battle", code=code) if code else redirect("home")


@login_required
def battle(request, code):
    return render(request, "quiz/battle.html", {"code": code.upper()})


@login_required
def leaderboard(request):
    return render(request, "quiz/leaderboard.html")


# ---------- REST API ----------
class QuestionListView(ListAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class LeaderboardView(APIView):
    def get(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        rows = (User.objects
                .annotate(wins=Count("matches_won", distinct=True),
                          played=Count("matches_as_p1", distinct=True) + Count("matches_as_p2", distinct=True))
                .filter(played__gt=0).order_by("-wins", "played")[:20])
        return Response([{"username": u.username, "wins": u.wins, "played": u.played} for u in rows])


class MyMatchesView(ListAPIView):
    serializer_class = MatchSerializer

    def get_queryset(self):
        u = self.request.user
        return Match.objects.filter(Q(player1=u) | Q(player2=u))[:20]
