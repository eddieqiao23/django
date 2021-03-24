from django.shortcuts import render
from django.http import HttpResponse

from .models import Question, Quiz

def index(request):
    quizzes = Quiz.objects.all()
    links = []
    for i in range(len(quizzes)):
        links.append("http://127.0.0.1:8000/quiz/%d/" % i)

    context = {
        'quizzes': quizzes,
        'links': links,
    }
    # return HttpResponse(output)
    return render(request, 'quiz/index.html', context)

def quiz_details(request, quiz_id):
    quiz = Quiz.objects.get(pk = quiz_id)

    context = {
        'curr_quiz': quiz,
    }

    return render(request, 'quiz/questions.html', context)

def results(request, quiz_id):
    return HttpResponse("results for quiz number " + str(quiz_id) + " would be here...  ")

def solutions(request, quiz_id):
    return HttpResponse("solutions for quiz number " + str(quiz_id) + " would be here...  ")
