from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from .models import Question, Quiz, Submission

from django.utils import timezone

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


def index(request):
    quizzes = Quiz.objects.all()

    failed = False

    if request.method == "POST" and "signup" in request.POST.keys():
        template = loader.get_template('quiz/signup.html')
        context = {}

        return HttpResponseRedirect(reverse('quiz:signup'))
    elif request.method == "POST":
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

def signup(request):
    print("hihi")
    template = loader.get_template('quiz/signup.html')
    diffPassword = False
    duplicateUser = False
    noUsername = False
    noPassword = False

    if request.method == "POST":
        print("hihi")
        if request.POST["inputPassword"] != request.POST["inputPasswordConfirm"]:
            diffPassword = True
        if User.objects.filter(username = request.POST["inputUsername"]).count() != 0:
            duplicateUser = True
        if len(request.POST["inputUsername"]) == 0:
            noUsername = True
        if len(request.POST["inputPassword"]) == 0 and len(request.POST["inputPasswordConfirm"]) == 0:
            noPassword = True

        context = {
            'diffPassword': diffPassword,
            'duplicateUser': duplicateUser,
            'noUsername': noUsername,
            'noPassword': noPassword
        }
        print(context)

        if (not diffPassword) and (not duplicateUser) and (not noUsername) and (not noPassword):
            print("ACC IS MADE")
            user = User.objects.create_user(
                username = request.POST["inputUsername"],
                password = request.POST["inputPassword"],
            )
            user.save()

            login_user = authenticate(username=request.POST['inputUsername'], password=request.POST['inputPassword'])

            if login_user is not None:
                login(request, login_user)
            else:
                print("SLKDFJLKSDFLKJSDJKF")

            return HttpResponseRedirect(reverse('quiz:index'))

        return HttpResponse(template.render(context, request))
    else:
        context = {
            'diffPassword': False,
            'duplicateUser': False,
            'noUsername': False,
            'noPassword': False
        }

        return HttpResponse(template.render(context, request))

    context = {
        'diffPassword': False,
        'duplicateUser': False,
        'noUsername': False,
        'noPassword': False
    }

    return HttpResponse(template.render(context, request))

def quiz_details(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk = quiz_id)
    past_final_subs = Submission.objects.filter(user = request.user, question__quiz__id = quiz_id, final_sub = True)

    subs_left = quiz.max_subs - past_final_subs.count() // quiz.quiz_length

    if request.method == "POST":
        for q in quiz.question_set.all():
            username = request.POST['userSubmitting']
            user = User.objects.filter(username = username)[0]
            is_final = "submit" in request.POST
            newSub = Submission(
                user = user,
                sub_time = timezone.now(),
                question = q,
                sub_answer = request.POST["answer" + str(q.id)],
                final_sub = is_final
            )

            newSub.save()

        if "save" in request.POST:
            context = {
                'curr_quiz': quiz,
                'subs_left': subs_left,
                'user': request.user,
                'validSubmission': False,
            }
            return HttpResponseRedirect(reverse('quiz:quiz_details', args = (quiz_id,)))
        else:
            return HttpResponseRedirect(reverse('quiz:result_details', args=(quiz_id,)))
    else:
        context = {
            'curr_quiz': quiz,
            'subs_left': subs_left,
            'user': request.user,
            'validSubmission': False,
        }
        return render(request, 'quiz/questions.html', context)


    context = {
        'curr_quiz': quiz,
        'subs_left': subs_left,
        'user': request.user,
        'validSubmission': True,
    }
    return render(request, 'quiz/questions.html', context)

def results(request):
    context = {
        'loggedIn': True
    }
    template = loader.get_template('quiz/results.html')

    
    return HttpResponse(template.render(context, request))

def result_details(request, quiz_id):
    if request.method == "POST":
        return HttpResponseRedirect(reverse('quiz:index'))

    curr_quiz = Quiz.objects.filter(id=quiz_id)[0]
    quiz_questions = curr_quiz.question_set.all()

    # Gets most recent submissions by this user for that quiz
    # Should be correct because for a quiz with n questions, there are n submissions in that order
    quiz_subs = Submission.objects.filter(user = request.user, question__quiz__id = quiz_id, final_sub = True)
    recent_subs = quiz_subs.order_by('sub_time')[len(quiz_subs) - len(quiz_questions):len(quiz_subs)]
    score = 0
    for sub in recent_subs:
        if sub.is_correct:
            score += 1

    context = {
        'recent_subs': recent_subs,
        'score': score,
    }

    template = loader.get_template('quiz/result_details.html')
    return HttpResponse(template.render(context, request))

def solutions(request, quiz_id):
    return HttpResponse("solutions for quiz number " + str(quiz_id) + " would be here...  ")
