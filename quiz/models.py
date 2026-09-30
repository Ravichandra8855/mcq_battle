from django.conf import settings
from django.db import models


class Question(models.Model):
    CHOICES = [("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")]
    text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct = models.CharField(max_length=1, choices=CHOICES)
    category = models.CharField(max_length=50, default="Python")

    def __str__(self):
        return self.text[:60]


class Match(models.Model):
    room_code = models.CharField(max_length=10)
    player1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="matches_as_p1")
    player2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="matches_as_p2")
    score1 = models.IntegerField(default=0)
    score2 = models.IntegerField(default=0)
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                               on_delete=models.SET_NULL, related_name="matches_won")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.player1} vs {self.player2} ({self.score1}-{self.score2})"
