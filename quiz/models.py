from django.db import models

class Quiz(models.Model):
    name = models.CharField(max_length=1000)
    # change this later to date allowed to see, question numbers, and allowed date

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete = models.CASCADE, default = 0)
    question_statement = models.CharField(max_length=200)
    answer = models.IntegerField(default=0) # Maybe change to string?
    solution = models.CharField(max_length=1000, default = "solution !")

    def __str__(self):
        return self.question_statement
