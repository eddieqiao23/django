from django.contrib import admin

from .models import Question, Quiz, Submission

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 3

class QuizAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Submission)
