from django.contrib import admin
from .models import (
    Teacher,
    Grade,
    Subject,
    Topic,
    Chapter,
    Student,
    StudentChapterCompletion,
    Quotes,
    ChapterQuiz,
    ChapterStudentResponse,
    ChapterQuestion,
    ChapterChoice,
)


class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "grade")


class TopicAdmin(admin.ModelAdmin):
    list_display = ("name", "subject")
    list_display_links = ("name", "subject")


class ChapterAdmin(admin.ModelAdmin):
    list_display = ("name", "topic")
    list_display_links = ("name", "topic")


class StudentAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "user", "grade")
    list_filter = ("user", "grade")
    search_fields = (
        "first_name",
        "last_name",
    )


class TeacherAdmin(admin.ModelAdmin):
    list_display = ("user", "grade")
    list_filter = ("user", "grade")
    search_fields = ("user",)


class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ("get_student_first_name", "get_chapter_name", "completed")
    list_filter = ("student", "chapter")

    def get_student_first_name(self, obj):
        return obj.student.first_name + " " + obj.student.last_name

    def get_chapter_name(self, obj):
        return obj.chapter.name


class QuotesAdmin(admin.ModelAdmin):
    list_display = ("quote", "author")


class ChapterChoiceInline(admin.TabularInline):
    model = ChapterChoice
    extra = 4


class ChapterQuestionAdmin(admin.ModelAdmin):
    inlines = [ChapterChoiceInline]



# Register your models here.
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Grade)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(StudentChapterCompletion, StudentProgressAdmin)
admin.site.register(Quotes, QuotesAdmin)
admin.site.register(ChapterQuiz)
admin.site.register(ChapterQuestion, ChapterQuestionAdmin)
admin.site.register(ChapterStudentResponse)