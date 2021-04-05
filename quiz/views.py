from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

from .models import Question, Quiz, Submission

from django.utils import timezone

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


def index(request):
    quizzes = Quiz.objects.all()

    failed = False

    if request.POST:
        if 'inputUsername' in request.POST.keys():
            user = authenticate(username=request.POST['inputUsername'], password=request.POST['inputPassword'])
            if user is not None:
                login(request, user)
            else:
                failed = True
                # failed login
        elif 'logout' in request.POST.keys():
            logout(request)
    if request.user.is_authenticated:
        loggedIn = True
    else:
        loggedIn = False

    template = loader.get_template('quiz/index.html')

    context = {
        'quizzes': quizzes,
        'loggedIn': loggedIn,
        'user': request.user,
        'failed': failed,
    }

    return HttpResponse(template.render(context, request))

def quiz_details(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk = quiz_id)

    if request.GET:
        print(request.GET)
        for q in quiz.question_set.all():
            print("LSDKFJSLKJDF" + str(q.id))
            username = request.GET['userSubmitting']
            print("username is: " + username)
            user = User.objects.filter(username = username)[0]
            newSub = Submission(
                user = user,
                sub_time = timezone.now(),
                question = q,
                sub_answer = request.GET['answer' + str(q.id)],
            )

            newSub.save()

    context = {
        'curr_quiz': quiz,
        'user': request.user
    }

    return render(request, 'quiz/questions.html', context)

def results(request, quiz_id):
    return HttpResponse("results for quiz number " + str(quiz_id) + " would be here...  ")

def solutions(request, quiz_id):
    return HttpResponse("solutions for quiz number " + str(quiz_id) + " would be here...  ")
