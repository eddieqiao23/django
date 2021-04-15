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

    if request.POST:
        print(request.POST)
        for q in quiz.question_set.all():
            print("LSDKFJSLKJDF" + str(q.id))
            username = request.POST['userSubmitting']
            print("username is: " + username)
            user = User.objects.filter(username = username)[0]
            newSub = Submission(
                user = user,
                sub_time = timezone.now(),
                question = q,
                sub_answer = request.POST['answer' + str(q.id)],
            )

            newSub.save()

        curr_quiz = Quiz.objects.filter(id=quiz_id)[0]
        quiz_questions = curr_quiz.question_set.all()

        quiz_subs = Submission.objects.filter(user = request.user, question__quiz__id = quiz_id)
        recent_subs = quiz_subs.order_by('-sub_time')[:quiz_questions.count()]
        context = {
            'recent_subs': recent_subs,
        }
        template = loader.get_template('quiz/results.html')
        return HttpResponse(template.render(context, request))

    context = {
        'curr_quiz': quiz,
        'user': request.user
    }
    return render(request, 'quiz/questions.html', context)

def results_index(request):
    return HttpResponse("results index...")

def results(request, quiz_id):
    curr_quiz = Quiz.objects.filter(id=quiz_id)[0]
    quiz_questions = curr_quiz.question_set.all()

    # Gets most recent submissions by this user for that quiz
    # Should be correct because for a quiz with n questions, there are n submissions in that order
    quiz_subs = Submission.objects.filter(user = request.user, question__quiz__id = quiz_id)
    recent_subs = quiz_subs.order_by('-sub_time')

    # for i in range(len(relevant_subs)):
    #     sub = relevant_subs[i]
    #     user_answers.append(sub.sub_answer)
    #     correct_answers.append(quiz_questions[i].answer)
    #     if sub.sub_answer == quiz_questions[i].answer:
    #         points.append(1) # Maybe allow for weighted questions
    #     else:
    #         points.append(0)

    print(recent_subs)

    context = {
        'recent_subs': recent_subs,
    }

    template = loader.get_template('quiz/results.html')
    return HttpResponse(template.render(context, request))

def solutions(request, quiz_id):
    return HttpResponse("solutions for quiz number " + str(quiz_id) + " would be here...  ")
