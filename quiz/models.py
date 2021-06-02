from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Quiz(models.Model):
    name = models.CharField(max_length=1000)
    description = models.CharField(max_length=300, default = "")
    max_subs = models.IntegerField(default = 99999)
    is_18_plus = models.BooleanField(default = False)

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
        return "%s submitted %s to question %d" % (self.user.username, self.sub_answer, self.question.id)

class UserAge(models.Model):
    user = models.OneToOneField(
        User,
        on_delete = models.CASCADE,
        primary_key = True
    )
    age = models.IntegerField(default = 0)

    @property
    def under_18(self):
        return self.age < 18

    def __str__(self):
        return "%s is %d" % (self.user.username, self.age)
