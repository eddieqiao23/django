from django.contrib import admin

from .models import Question, Quiz, Submission, UserAge

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 3

class QuizAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Submission)
admin.site.register(UserAge)
