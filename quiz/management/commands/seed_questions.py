from django.core.management.base import BaseCommand
from quiz.models import Question

DATA = [
    ("Which keyword defines a function in Python?", "func", "def", "define", "lambda", "B"),
    ("What is the output of type([])?", "<class 'list'>", "<class 'tuple'>", "<class 'dict'>", "<class 'set'>", "A"),
    ("Which data type is immutable in Python?", "list", "dict", "tuple", "set", "C"),
    ("What does len('Django') return?", "5", "6", "7", "Error", "B"),
    ("Which command creates a new Django project?", "django-admin startproject", "python manage.py runserver", "django new", "pip install django", "A"),
    ("Django follows which architectural pattern?", "MVC only", "MTV", "MVVM", "Microservices", "B"),
    ("Which file holds Django URL routes?", "views.py", "models.py", "urls.py", "admin.py", "C"),
    ("Which command applies DB migrations?", "makemigrations", "migrate", "syncdb", "runmigrations", "B"),
    ("Which HTTP method is used to create a resource in REST?", "GET", "PUT", "DELETE", "POST", "D"),
    ("Which HTTP status code means 'Not Found'?", "200", "301", "404", "500", "C"),
    ("What does ORM stand for?", "Object Relational Mapping", "Online Resource Manager", "Object Request Model", "Open Relation Method", "A"),
    ("Which Python feature yields values lazily?", "Generator", "Decorator", "Class", "Module", "A"),
    ("Which symbol starts a comment in Python?", "//", "#", "/*", "--", "B"),
    ("Which DRF class provides a ready-made list endpoint?", "ListAPIView", "HttpResponse", "FormView", "TemplateView", "A"),
    ("What is the time complexity of dict lookup on average?", "O(n)", "O(log n)", "O(1)", "O(n log n)", "C"),
    ("Which Git command uploads commits to GitHub?", "git pull", "git push", "git clone", "git fetch", "B"),
    ("Which HTML tag creates a hyperlink?", "<link>", "<a>", "<href>", "<url>", "B"),
    ("Which CSS property changes text colour?", "font-color", "text-style", "color", "foreground", "C"),
    ("Which JavaScript method parses a JSON string?", "JSON.parse()", "JSON.stringify()", "JSON.load()", "parseJSON()", "A"),
    ("Which SQL clause filters rows?", "ORDER BY", "GROUP BY", "WHERE", "LIMIT", "C"),
    ("Which structure is FIFO?", "Stack", "Queue", "Tree", "Graph", "B"),
    ("What does CRUD stand for?", "Create Read Update Delete", "Copy Run Undo Deploy", "Connect Route Use Debug", "Create Render Update Deploy", "A"),
]


class Command(BaseCommand):
    help = "Load sample MCQs"

    def handle(self, *args, **opts):
        for t, a, b, c, d, ans in DATA:
            Question.objects.get_or_create(text=t, defaults=dict(option_a=a, option_b=b, option_c=c, option_d=d, correct=ans))
        self.stdout.write(self.style.SUCCESS(f"{Question.objects.count()} questions in DB"))
