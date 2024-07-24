from django.urls import path
from . import views

urlpatterns = [
    # GENERAL URLS
    path("", views.index_learn, name="index_learn"),






    # USER URLS
    path("dashboard", views.user_dashboard, name="user_dashboard"),
    path("manage-grades", views.manage_grade, name="manage_grades"),
    path("<str:student_slug>", views.student_dashboard, name="student_dashboard"),
    path(
        "<str:student_slug>/<str:subject_slug>",
        views.subject_dashboard,
        name="subject_dashboard",
    ),
    path(
        "<str:student_slug>/<str:subject_slug>/<str:topic_slug>",
        views.topic_dashboard,
        name="topic_dashboard",
    ),
    path(
        "<str:student_slug>/<str:subject_slug>/<str:topic_slug>/<str:chapter_slug>/overview",
        views.chapter_dashboard,
        name="chapter_dashboard",
    ),
    path(
        "<str:student_slug>/<str:subject_slug>/<str:topic_slug>/<str:chapter_slug>",
        views.chapter_content,
        name="chapter_content",
    ),




    # CHAPTER QUIZ URLS
    path(
        "<str:student_slug>/<str:subject_slug>/<str:topic_slug>/<str:chapter_slug>/<str:quiz_slug>/overview",
        views.chapter_quiz_overview,
        name="chapter_quiz_overview",
    ),

    path(
        "<str:student_slug>/<str:subject_slug>/<str:topic_slug>/<str:chapter_slug>/<str:quiz_slug>",
        views.chapter_quiz_content,
        name="chapter_quiz_content",
    ),

    path(
        "<str:student_slug>/<str:subject_slug>/<str:topic_slug>/<str:chapter_slug>/<str:quiz_slug>/submit",
        views.chapter_quiz_submit,
        name="chapter_quiz_submit",
    ),

    path(
        "<str:student_slug>/<str:subject_slug>/<str:topic_slug>/<str:chapter_slug>/<str:quiz_slug>/results",
        views.chapter_quiz_results,
        name="chapter_quiz_results",
    ),

]
