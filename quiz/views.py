from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from .models import Question, Quiz

def index(request):
    quizzes = Quiz.objects.all()

    context = {
        'quizzes': quizzes,
    }
    # return HttpResponse(output)
    return render(request, 'quiz/index.html', context)

def quiz_details(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk = quiz_id)

    context = {
        'curr_quiz': quiz,
    }

    return render(request, 'quiz/questions.html', context)

def results(request, quiz_id):
    return HttpResponse("results for quiz number " + str(quiz_id) + " would be here...  ")

def solutions(request, quiz_id):
    return HttpResponse("solutions for quiz number " + str(quiz_id) + " would be here...  ")
