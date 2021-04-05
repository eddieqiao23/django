from django.db import models
from django.contrib.auth.models import User

class Quiz(models.Model):
    name = models.CharField(max_length=1000)

    def __str__(self):
        return self.name
    # change this later to date allowed to see, question numbers, and allowed date

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete = models.CASCADE, default = 0)
    question_statement = models.CharField(max_length=200)
    answer = models.IntegerField(default=0) # Maybe change to string?
    solution = models.CharField(max_length=1000, default = "solution !")

    def __str__(self):
        return self.question_statement

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    sub_time = models.DateTimeField("date submitted")
    question = models.ForeignKey(Question, on_delete = models.CASCADE)
    sub_answer = models.IntegerField(default = 0)

    def __str__(self):
        return self.user.username + " submitted " + str(self.sub_answer) + " to question " + str(self.question.id)
