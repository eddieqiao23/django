from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Quiz(models.Model):
    name = models.CharField(max_length=1000)
    description = models.CharField(max_length=300, default = "")
    max_subs = models.IntegerField(default = 99999)

    @property
    def quiz_length(self):
        return Question.objects.filter(quiz = self).count()

    def __str__(self):
        return self.name

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete = models.CASCADE, default = 0)
    question_statement = models.CharField(max_length = 750)
    answer = models.CharField(default = "", max_length = 30)

    @property
    def last_sub(self):
        return Submission.objects.filter(question = self).order_by("-sub_time")[0]

    def __str__(self):
        return self.question_statement

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    sub_time = models.DateTimeField("date submitted")
    question = models.ForeignKey(Question, on_delete = models.CASCADE)
    sub_answer = models.CharField(default = "", max_length = 250)
    final_sub = models.BooleanField(default = True)

    @property
    def is_correct(self):
        return self.sub_answer == self.question.answer

    def __str__(self):
        return self.user.username + " submitted " + str(self.sub_answer) + " to question " + str(self.question.id)
