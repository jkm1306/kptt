from django.shortcuts import render
from django.shortcuts import redirect
from .forms import StudentGradeFormSet, StudentProgressForm
from .models import (
    Student,
    Subject,
    Topic,
    Chapter,
    StudentChapterCompletion,
    ChapterQuiz,
    ChapterQuestion,
    ChapterChoice,
    ChapterStudentResponse,
    Quotes,
)
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils.http import urlencode
from django.urls import reverse


# Create your views here.
def index_learn(request):

    return render(request, "index_learn.html")


@login_required
def user_dashboard(request):
    student = Student.objects.filter(user=request.user)
    number_of_students = student.count()

    context = {
        "student": student,
        "number_of_students": number_of_students,
    }

    return render(request, "main_user_dashboard.html", context=context)


@login_required
def manage_grade(request):
    if request.method == "POST":
        formset = StudentGradeFormSet(request.POST, request.FILES)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.user = request.user  # Set the user for each instance
                instance.save()
            return redirect("user_dashboard")  # Redirect to a new URL
    else:
        formset = StudentGradeFormSet(queryset=Student.objects.none())
    # No pre-filled forms
    return render(request, "manage_grade.html", {"formset": formset})


@login_required
def student_dashboard(request, student_slug):
    student = get_object_or_404(Student, student_slug=student_slug)
    subjects = Subject.objects.filter(grade=student.grade)

    content = {
        "student": student,
        "subjects": subjects,
    }

    return render(request, "student/dashboard.html", content)


@login_required
def subject_dashboard(request, subject_slug, student_slug):
    student = get_object_or_404(Student, student_slug=student_slug)
    subject = get_object_or_404(Subject, subject_slug=subject_slug, grade=student.grade)
    topics = Topic.objects.filter(subject=subject)
    number_of_topics = topics.count()

    topic_data = []
    fully_completed_topics = 0
    for topic in topics:
        chapters = Chapter.objects.filter(topic=topic)
        completed_chapters = StudentChapterCompletion.objects.filter(
            student=student, chapter__in=chapters, completed=True
        ).values_list("chapter__id", flat=True)
        num_completed_chapters = completed_chapters.count()
        num_total_chapters = chapters.count()

        if num_total_chapters > 0:
            completion_percentage = round(
                (num_completed_chapters / num_total_chapters) * 100
            )
        else:
            completion_percentage = 0

        topic_data.append(
            {
                "topic": topic,
                "num_completed_chapters": num_completed_chapters,
                "num_total_chapters": num_total_chapters,
                "completion_percentage": completion_percentage,
            }
        )

        if completion_percentage == 100:
            fully_completed_topics += 1

        subject_completion_percentage = round(
            (fully_completed_topics / number_of_topics) * 100
        )

    context = {
        "student": student,
        "subject": subject,
        "topics": topics,
        "topic_data": topic_data,
        "number_of_topics": number_of_topics,
        "fully_completed_topics": fully_completed_topics,
        "subject_completion_percentage": subject_completion_percentage,
    }

    return render(request, "student/subject/dashboard.html", context)


def subject_details(request, subject_slug, student_slug, topic_slug):
    student = get_object_or_404(Student, student_slug=student_slug)
    subject = get_object_or_404(Subject, subject_slug=subject_slug, grade=student.grade)
    topics = Topic.objects.filter(subject=subject)

    number_of_topics = topics.count()

    specific_topic = Topic.objects.get(topic_slug=topic_slug)
    chapters_for_topic = specific_topic.objects.filter(topic=specific_topic)

    content = {
        "subject": subject,
        "topics": topics,
        "student": student,
        "number_of_topics": number_of_topics,
        "chapters_for_topic": chapters_for_topic,
    }

    return render(request, "student/subject/details.html", content)


def dashboard_subject_details(request, subject_slug, student_slug, topic_slug):
    student = get_object_or_404(Student, student_slug=student_slug)
    subject = get_object_or_404(Subject, subject_slug=subject_slug, grade=student.grade)
    topics = Topic.objects.filter(subject=subject)

    number_of_topics = topics.count()

    topic = Topic.objects.get(topic_slug=topic_slug)
    chapters = Chapter.objects.filter(topic=topic)

    completed_chapters = StudentChapterCompletion.objects.filter(
        student=student, chapter__in=chapters, completed=True
    ).values_list("chapter__id", flat=True)

    content = {
        "subject": subject,
        "topics": topics,
        "student": student,
        "number_of_topics": number_of_topics,
    }

    return render(request, "student/include/subject_details.html", content)


# TOPIC VIEWS
def topic_dashboard(request, student_slug, subject_slug, topic_slug):
    student = Student.objects.get(student_slug=student_slug)
    subject = Subject.objects.get(subject_slug=subject_slug)
    topic = Topic.objects.get(topic_slug=topic_slug)
    chapters = Chapter.objects.filter(topic=topic)
    chapter_order = chapters.order_by("number")

    number_of_chapters = chapters.count()

    completed_chapters = StudentChapterCompletion.objects.filter(
        student=student, chapter__in=chapters, completed=True
    ).values_list("chapter__id", flat=True)

    number_of_completed_chapters = completed_chapters.count()

    if number_of_chapters > 0:
        completion_percentage = round(
            (number_of_completed_chapters / number_of_chapters) * 100
        )
    else:
        completion_percentage = 0

    context = {
        "student": student,
        "subject": subject,
        "topic": topic,
        "chapters": chapters,
        "subject_slug": subject_slug,
        "chapter_order": chapter_order,
        "number_of_chapters": number_of_chapters,
        "number_of_completed_chapters": number_of_completed_chapters,
        "completion_percentage": completion_percentage,
    }
    return render(request, "student/topic/dashboard.html", context)


# CHAPTER VIEWS
@login_required
def chapter_dashboard(request, student_slug, subject_slug, topic_slug, chapter_slug):
    student = Student.objects.get(student_slug=student_slug)
    subject = Subject.objects.filter(subject_slug=subject_slug)
    topic = Topic.objects.get(topic_slug=topic_slug)
    chapters = Chapter.objects.filter(topic=topic)

    single_subject = subject.get(subject_slug=subject_slug)
    single_chapter = chapters.get(chapter_slug=chapter_slug)

    chapter_status, created = StudentChapterCompletion.objects.get_or_create(
        student=student, chapter=single_chapter
    )

    quizzes = ChapterQuiz.objects.filter(chapter=single_chapter)

    context = {
        "student": student,
        "subject": subject,
        "topic": topic,
        "chapters": chapters,
        "subject_slug": subject_slug,
        "chapter_slug": chapter_slug,
        "single_subject": single_subject,
        "single_chapter": single_chapter,
        "chapter_status": chapter_status,
        "quizzes": quizzes,
    }
    return render(request, "student/chapter/dashboard.html", context)


@login_required
def chapter_content(request, student_slug, subject_slug, topic_slug, chapter_slug):
    student = Student.objects.get(student_slug=student_slug)
    subject = Subject.objects.filter(subject_slug=subject_slug)
    topic = Topic.objects.get(topic_slug=topic_slug)
    chapters = Chapter.objects.filter(topic=topic)

    single_subject = subject.get(subject_slug=subject_slug)
    single_chapter = chapters.get(chapter_slug=chapter_slug)

    next_chapter = (
        chapters.filter(number__gt=single_chapter.number).order_by("number").first()
    )
    prev_chapter = (
        chapters.filter(number__lt=single_chapter.number).order_by("number").last()
    )

    chapter_status, created = StudentChapterCompletion.objects.get_or_create(
        student=student, chapter=single_chapter
    )

    if request.method == "POST":
        form = StudentProgressForm(request.POST, instance=chapter_status)
        if form.is_valid():
            form.save()
            return redirect(
                "chapter_dashboard",
                student_slug,
                subject_slug,
                topic_slug,
                chapter_slug,
            )
    else:
        form = StudentProgressForm(instance=chapter_status)

    quizzes = ChapterQuiz.objects.filter(chapter=single_chapter)

    context = {
        "student": student,
        "subject": subject,
        "topic": topic,
        "chapters": chapters,
        "subject_slug": subject_slug,
        "chapter_slug": chapter_slug,
        "next_chapter": next_chapter,
        "prev_chapter": prev_chapter,
        "single_subject": single_subject,
        "single_chapter": single_chapter,
        "chapter_completion_form": form,
        "chapter_status": chapter_status,
        "quizzes": quizzes,
    }
    return render(request, "student/chapter/content/content.html", context)


# CHAPTER QUIZ VIEWS
@login_required(login_url="login")
def chapter_quiz_overview(
    request, student_slug, subject_slug, topic_slug, chapter_slug, quiz_slug
):
    student = get_object_or_404(Student, student_slug=student_slug)
    subject = get_object_or_404(Subject, subject_slug=subject_slug)
    topic = get_object_or_404(Topic, topic_slug=topic_slug, subject=subject)
    chapter = get_object_or_404(Chapter, chapter_slug=chapter_slug, topic=topic)
    quiz = get_object_or_404(ChapterQuiz, quiz_slug=quiz_slug, chapter=chapter)
    questions = ChapterQuestion.objects.filter(quiz=quiz)
    responses = ChapterStudentResponse.objects.filter(quiz=quiz, student=student)
    quizzes = ChapterQuiz.objects.filter(chapter=chapter)

    time_min = round(quiz.duration / 60)

    quiz_submitted = ChapterStudentResponse.objects.filter(
        student=student, quiz=quiz
    ).exists()

    correct_choices = 0
    incorrect_choices = 0
    selected_choices = {}
    correct_questions = []
    incorrect_questions = []

    for response in responses:
        question = response.question
        selected_choice = response.choice
        selected_choices[question] = selected_choice

        if selected_choice.is_correct:
            correct_choices += 1
            correct_questions.append(question)
        else:
            incorrect_choices += 1
            incorrect_questions.append(question)

    if len(questions) == 0:
        percentage = 0
    else:
        percentage = round((correct_choices / len(questions)) * 100)

    number_correct = len(correct_questions)
    number_incorrect = len(incorrect_questions)

    context = {
        "student": student,
        "subject": subject,
        "topic": topic,
        "chapter": chapter,
        "quizzes": quizzes,
        "quiz": quiz,
        "questions": questions,
        "selected_choices": selected_choices,
        "correct_choices": correct_choices,
        "incorrect_choices": incorrect_choices,
        "number_correct": number_correct,
        "number_incorrect": number_incorrect,
        "percentage": percentage,
        "quiz_submitted": quiz_submitted,
        "time_min": time_min,
    }
    return render(request, "student/chapter/quizzes/dashboard.html", context)


@login_required(login_url="login")
def chapter_quiz_content(
    request,
    student_slug,
    subject_slug,
    topic_slug,
    chapter_slug,
    quiz_slug,
):
    student = get_object_or_404(Student, student_slug=student_slug)
    subject = get_object_or_404(Subject, subject_slug=subject_slug)
    topic = get_object_or_404(Topic, topic_slug=topic_slug, subject=subject)
    chapter = get_object_or_404(Chapter, chapter_slug=chapter_slug, topic=topic)

    quizzes = ChapterQuiz.objects.filter(chapter=chapter)
    quiz = get_object_or_404(ChapterQuiz, quiz_slug=quiz_slug, chapter=chapter)

    questions = ChapterQuestion.objects.filter(quiz=quiz)

    context = {
        "student": student,
        "subject": subject,
        "topic": topic,
        "chapter": chapter,
        "quizzes": quizzes,
        "quiz": quiz,
        "questions": questions,
    }
    return render(request, "student/chapter/quizzes/content.html", context)


@login_required(login_url="login")
def chapter_quiz_questions(
    request,
    student_slug,
    subject_slug,
    topic_slug,
    chapter_slug,
    quiz_slug,
    question_id,
):
    student = get_object_or_404(Student, student_slug=student_slug)
    subject = get_object_or_404(Subject, subject_slug=subject_slug)
    topic = get_object_or_404(Topic, topic_slug=topic_slug, subject=subject)
    chapter = get_object_or_404(Chapter, chapter_slug=chapter_slug, topic=topic)

    quizzes = ChapterQuiz.objects.filter(chapter=chapter)
    quiz = get_object_or_404(ChapterQuiz, quiz_slug=quiz_slug, chapter=chapter)

    questions = ChapterQuestion.objects.filter(quiz=quiz)

    question = ChapterQuestion.objects.get(id=question_id)

    context = {
        "student": student,
        "subject": subject,
        "topic": topic,
        "chapter": chapter,
        "quizzes": quizzes,
        "quiz": quiz,
        "questions": questions,
        "question_ans": question,
    }

    return render(request, "student/chapter/quizzes/content.html", context)


@login_required(login_url="login")
def chapter_quiz_submit(
    request, student_slug, subject_slug, topic_slug, chapter_slug, quiz_slug
):
    student = get_object_or_404(Student, student_slug=student_slug)
    subject = get_object_or_404(Subject, subject_slug=subject_slug)
    topic = get_object_or_404(Topic, topic_slug=topic_slug, subject=subject)
    chapter = get_object_or_404(Chapter, chapter_slug=chapter_slug, topic=topic)
    quiz = get_object_or_404(ChapterQuiz, quiz_slug=quiz_slug)
    questions = ChapterQuestion.objects.filter(quiz=quiz)

    if request.method == "POST":
        # Delete previous responses for this student and quiz
        ChapterStudentResponse.objects.filter(student=student, quiz=quiz).delete()

        # Process the form data
        score = 0
        total_questions = len(questions)
        unanswered_questions = []

        for question in questions:
            answer_id = request.POST.get(str(question.id))
            if answer_id:
                # Check if the answer is correct
                choice = get_object_or_404(ChapterChoice, id=answer_id)
                ChapterStudentResponse.objects.create(
                    student=student,
                    question=question,
                    quiz=quiz,
                    choice=choice,
                )
                if choice.is_correct:
                    score += 1
            else:
                # Unanswered question
                unanswered_questions.append(question)

        # Calculate the percentage score
        percentage_score = round((score / total_questions) * 100)

        query_params = {
            "score": score,
            "total_questions": total_questions,
            "unanswered_questions": ",".join([str(q.id) for q in unanswered_questions]),
            "percentage_score": percentage_score,
        }
        redirect_url = f"{reverse('chapter_quiz_results', args=[student_slug, subject_slug, topic_slug, chapter_slug, quiz_slug])}?{urlencode(query_params)}"
        return redirect(redirect_url)

    context = {
        "student": student,
        "subject": subject,
        "topic": topic,
        "chapter": chapter,
        "quiz": quiz,
        "questions": questions,
    }
    return render(request, "student/chapter/quizzes/questions.html", context)


@login_required(login_url="login")
def chapter_quiz_results(
    request, student_slug, subject_slug, topic_slug, chapter_slug, quiz_slug
):
    student = get_object_or_404(Student, student_slug=student_slug)
    subject = get_object_or_404(Subject, subject_slug=subject_slug)
    topic = get_object_or_404(Topic, topic_slug=topic_slug, subject=subject)
    chapter = get_object_or_404(Chapter, chapter_slug=chapter_slug, topic=topic)
    quiz = get_object_or_404(ChapterQuiz, quiz_slug=quiz_slug, chapter=chapter)
    questions = ChapterQuestion.objects.filter(quiz=quiz)
    responses = ChapterStudentResponse.objects.filter(quiz=quiz, student=student)
    quizzes = ChapterQuiz.objects.filter(chapter=chapter)

    correct_choices = 0
    incorrect_choices = 0
    selected_choices = {}
    correct_questions = []
    incorrect_questions = []

    for response in responses:
        question = response.question
        selected_choice = response.choice
        selected_choices[question] = selected_choice

        if selected_choice.is_correct:
            correct_choices += 1
            correct_questions.append(question)
        else:
            incorrect_choices += 1
            incorrect_questions.append(question)
    
    number_unanswered_questions = len(questions) - len(responses)


    unanswered_questions = []
    answered_question_ids = [response.question.id for response in responses]
    for question in questions.exclude(id__in=answered_question_ids):
        choices = list(question.choices.values('id', 'choice_text', 'is_correct', 'explanation'))
        unanswered_questions.append({
            'question_text': question.question_text,
            'choices': choices
        })



    if len(questions) == 0:
        percentage = 0
    else:
        percentage = round((correct_choices / len(questions)) * 100)


    number_correct = len(correct_questions)
    number_incorrect = len(incorrect_questions)

    if percentage >= 100:
        color = "#05A000"
    elif percentage >= 90:
        color = "#07D100"
    elif percentage >= 80:
        color = "#08FB00"
    elif percentage >= 75:
        color = "#51FF00"
    elif percentage >= 60:
        color = "#ECC100"
    elif percentage >= 50:
        color = "#EC8B00"
    elif percentage >= 40:
        color = "#BF5700"
    elif percentage >= 30:
        color = "#F73100"
    elif percentage >= 0:
        color = "#FF0000"

    context = {
        "student": student,
        "subject": subject,
        "topic": topic,
        "chapter": chapter,
        "quiz": quiz,
        "questions": questions,
        "responses": responses,
        "correct_choices": correct_choices,
        "percentage": percentage,
        "color": color,
        "incorrect_choices": incorrect_choices,
        "selected_choices": selected_choices,
        "correct_questions": correct_questions,
        "incorrect_questions": incorrect_questions,
        "number_correct": number_correct,
        "number_incorrect": number_incorrect,
        "quizzes": quizzes,
        "unanswered_questions": unanswered_questions,
        "number_unanswered": number_unanswered_questions,
    }
    return render(request, "student/chapter/quizzes/results.html", context)


# End Line
