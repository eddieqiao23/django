from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import View

from .models import Question, Quiz, Submission

from django.utils import timezone

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

class IndexView(View):
    def get(self, request):
        quizzes = Quiz.objects.all()
        template = loader.get_template('quiz/index.html')
        if request.user.is_authenticated:
            loggedIn = True
        else:
            loggedIn = False

        context = {
            'quizzes': quizzes,
            'loggedIn': loggedIn,
            'user': request.user
        }

        return HttpResponse(template.render(context, request))


    def post(self, request):
        quizzes = Quiz.objects.all()
        failed = False
        template = loader.get_template('quiz/index.html')
        loggedIn = False

        if "signup" in request.POST.keys():
            return HttpResponseRedirect(reverse('quiz:signup'))
        elif 'logout' in request.POST.keys():
            logout(request)
        else:
            user = authenticate(username=request.POST['inputUsername'], password=request.POST['inputPassword'])
            if user is not None:
                login(request, user)
                loggedIn = True
            else:
                failed = True


        context = {
            'quizzes': quizzes,
            'loggedIn': loggedIn,
            'user': request.user,
            'failed': failed
        }

        return HttpResponse(template.render(context, request))

class SignupView(View):
    def get(self, request):
        template = loader.get_template('quiz/signup.html')
        context = {
            'diffPassword': False,
            'duplicateUser': False,
            'noUsername': False,
            'noPassword': False
        }

        return HttpResponse(template.render(context, request))

    def post(self, request):
        template = loader.get_template('quiz/signup.html')
        diffPassword = False
        duplicateUser = False
        noUsername = False
        noPassword = False

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

        if (not diffPassword) and (not duplicateUser) and (not noUsername) and (not noPassword):
            user = User.objects.create_user(
                username = request.POST["inputUsername"],
                password = request.POST["inputPassword"],
            )
            user.save()

            login_user = authenticate(username=request.POST['inputUsername'], password=request.POST['inputPassword'])

            if login_user is not None:
                login(request, login_user)
            else:
                return HttpResponse("If you reach this page I failed :(")

            return HttpResponseRedirect(reverse('quiz:index'))
        else:
            context = {
                'diffPassword': diffPassword,
                'duplicateUser': duplicateUser,
                'noUsername': noUsername,
                'noPassword': noPassword,
                'prefill_vals': [request.POST["inputUsername"], request.POST["inputPassword"], request.POST["inputPasswordConfirm"]],
            }


        return HttpResponse(template.render(context, request))

class QuizDetailsView(View):
    def get(self, request, quiz_id):
        if Quiz.objects.filter(id = quiz_id).count() == 0:
            context = {
                'quiz_exists': False
            }
        else:
            quiz = Quiz.objects.get(id = quiz_id)

            past_final_subs = Submission.objects.filter(user = request.user, question__quiz__id = quiz_id, final_sub = True)
            subs_left = quiz.max_subs - past_final_subs.count() // quiz.quiz_length

            need_prefill = False
            prefill_vals = []
            data = []
            questions = Question.objects.filter(quiz = quiz)

            for q in questions:
                curr_data = [q.question_statement, q.id]
                if Submission.objects.filter(question = q, user = request.user).count() == 0:
                    curr_data.append("")
                else:
                    last_sub = Submission.objects.filter(question = q, user = request.user).order_by("-sub_time")[0]
                    if last_sub.final_sub:
                        curr_data.append("")
                    else:
                        curr_data.append(last_sub.sub_answer)

                data.append(curr_data)

            context = {
                'curr_quiz': quiz,
                'subs_left': subs_left,
                'user': request.user,
                'validSubmission': False,
                'data': data,
                'quiz_exists': True,
            }
        return render(request, 'quiz/quiz_details.html', context)

    def post(self, request, quiz_id):
        if 'logout' in request.POST:
            logout(request)
            return HttpResponseRedirect(reverse('quiz:index'))

        quiz = get_object_or_404(Quiz, pk = quiz_id)

        past_final_subs = Submission.objects.filter(user = request.user, question__quiz__id = quiz_id, final_sub = True)
        subs_left = quiz.max_subs - past_final_subs.count() // quiz.quiz_length

        for q in quiz.question_set.all():
            username = request.POST['userSubmitting']
            user = User.objects.filter(username = username)[0]
            is_final = 'submit' in request.POST
            newSub = Submission(
                user = user,
                sub_time = timezone.now(),
                question = q,
                sub_answer = request.POST['answer' + str(q.id)],
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

class ResultsView(View):
    def get(self, request):
        template = loader.get_template('quiz/results.html')
        quizzes = []

        for quiz in Quiz.objects.all():
            past_subs = Submission.objects.filter(user=request.user, question__quiz=quiz, final_sub=True)
            if past_subs.count() != 0:
                quizzes.append(quiz)

        context = {
            'loggedIn': True,
            'quizzes': quizzes,
        }

        return HttpResponse(template.render(context, request))

    def post(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('quiz:index'))

class ResultDetailsView(View):
    def get(self, request, quiz_id):
        quiz_exists = True
        if Quiz.objects.filter(id = quiz_id).count() == 0:
            context = {
                'quiz_exists': False
            }
        else:
            curr_quiz = Quiz.objects.filter(id=quiz_id)[0]
            quiz_questions = curr_quiz.question_set.all()

            # Gets most recent submissions by this user for that quiz
            # Should be correct because for a quiz with n questions, there are n submissions in that order
            quiz_subs = Submission.objects.filter(user = request.user, question__quiz__id = quiz_id, final_sub = True)
            print(quiz_subs)
            print(len(quiz_questions))
            recent_subs = quiz_subs.order_by('sub_time')[len(quiz_subs) - len(quiz_questions):len(quiz_subs)]
            score = 0
            for sub in recent_subs:
                if sub.is_correct:
                    score += 1

            context = {
                'recent_subs': recent_subs,
                'score': score,
                'quiz_exists': True
            }

        template = loader.get_template('quiz/result_details.html')
        return HttpResponse(template.render(context, request))

    def post(self, request, quiz_id):
        return HttpResponseRedirect(reverse('quiz:results'))

class TestPageView(View):
    def get(self, request):
        template = loader.get_template('quiz/test.html')
        context = {
            'array': [1, 2, 3],
        }
        return HttpResponse(template.render(context, request))
