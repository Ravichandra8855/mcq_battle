from rest_framework import serializers
from .models import Match, Question


class QuestionSerializer(serializers.ModelSerializer):
    """Correct answer is intentionally NOT exposed."""
    class Meta:
        model = Question
        fields = ["id", "text", "option_a", "option_b", "option_c", "option_d", "category"]


class MatchSerializer(serializers.ModelSerializer):
    player1 = serializers.CharField(source="player1.username")
    player2 = serializers.CharField(source="player2.username")
    winner = serializers.CharField(source="winner.username", default=None)

    class Meta:
        model = Match
        fields = ["id", "room_code", "player1", "player2", "score1", "score2", "winner", "created_at"]
