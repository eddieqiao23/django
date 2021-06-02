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
        # The get method just loads the index
        quizzes = Quiz.objects.all()
        template = loader.get_template('quiz/index.html')
        # Creates different pages if logged in or not
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
        failed = False # Error message if wrong password or something
        template = loader.get_template('quiz/index.html')
        loggedIn = False

        # Checks if signup, logout, or login was pressed
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
                # Wrong password or something
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
        # Just loads the page
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
        # Possible error messages when signing up
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
            # If everything works out, try creating the user
            user = User.objects.create_user(
                username = request.POST["inputUsername"],
                password = request.POST["inputPassword"],
            )
            user.save()

            # Tries to log the user in
            login_user = authenticate(username=request.POST['inputUsername'], password=request.POST['inputPassword'])
            if login_user is not None:
                login(request, login_user)
            else:
                return HttpResponse("If you reach this page I failed :(")

            return HttpResponseRedirect(reverse('quiz:index'))
        else:
            # Sends the error messages and the values so that the form doesn't clear
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
        if not(request.user.is_authenticated):
            return HttpResponseRedirect(reverse('quiz:index'))

        # Makes sure the quiz actually exists
        if Quiz.objects.filter(id = quiz_id).count() == 0:
            context = {
                'quiz_exists': False
            }
        else:
            # Gets the quiz (doesn't need error message since we know it exists)
            quiz = Quiz.objects.get(id = quiz_id)

            # Determines submissions already used
            past_final_subs = Submission.objects.filter(user = request.user, question__quiz__id = quiz_id, final_sub = True)
            subs_left = quiz.max_subs - past_final_subs.count() // quiz.quiz_length

            # If the user saved answers before but didn't submit, then prefill
            need_prefill = False
            prefill_vals = []
            data = []
            questions = Question.objects.filter(quiz = quiz)

            # Data stores question statements and IDs, which makes it easier later
            for q in questions:
                curr_data = [q.question_statement, q.id]
                # If not submission before
                if Submission.objects.filter(question = q, user = request.user).count() == 0:
                    curr_data.append("")
                else:
                    last_sub = Submission.objects.filter(question = q, user = request.user).order_by("-sub_time")[0]
                    # If the last submission was "submit," thenno prefill
                    if last_sub.final_sub:
                        curr_data.append("")
                    # Otherwise, it was a saved answer
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
        # This could be logout, save, or submit
        if 'logout' in request.POST:
            logout(request)
            return HttpResponseRedirect(reverse('quiz:index'))

        # Determines how many submissions the user has left
        quiz = get_object_or_404(Quiz, pk = quiz_id)
        past_final_subs = Submission.objects.filter(user = request.user, question__quiz__id = quiz_id, final_sub = True)
        subs_left = quiz.max_subs - past_final_subs.count() // quiz.quiz_length

        for q in quiz.question_set.all():
            username = request.POST['userSubmitting']
            user = User.objects.filter(username = username)[0]
            # "submit" = True, "save" = False
            is_final = 'submit' in request.POST

            # Creates the new submission and saves it
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
        if not(request.user.is_authenticated):
            return HttpResponseRedirect(reverse('quiz:index'))

        template = loader.get_template('quiz/results.html')
        quizzes = []

        # Gets the quizzes that the user has submitted answers for
        for quiz in Quiz.objects.all():
            past_subs = Submission.objects.filter(user=request.user, question__quiz=quiz, final_sub=True)
            if past_subs.count() != 0:
                quizzes.append(quiz)

        context = {
            'quizzes': quizzes,
        }

        return HttpResponse(template.render(context, request))

    def post(self, request):
        # The only possibliity is that "logout" was clicked, so it logs the user out
        logout(request)
        return HttpResponseRedirect(reverse('quiz:index'))

class ResultDetailsView(View):
    def get(self, request, quiz_id):
        if not(request.user.is_authenticated):
            return HttpResponseRedirect(reverse('quiz:index'))

        # Checks if the quiz exists
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
            recent_subs = quiz_subs.order_by('sub_time')[len(quiz_subs) - len(quiz_questions):len(quiz_subs)]

            # Calculates score
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
        # If the user is logging out then log them out
        if 'logout' in request.POST.keys():
            logout(request)
            return HttpResponseRedirect(reverse('quiz:index'))
        # Otherwise just open the results page
        else:
            return HttpResponseRedirect(reverse('quiz:results'))
