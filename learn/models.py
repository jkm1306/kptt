from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError


COLORS = {
    "#0284c7": "blue",
    "#0bb801": "green",
    "#ffea00": "yellow",
    "#df0000": "red",
    "#5900df": "purple",
    "#616161": "gray",
    "#e300c5": "pink",
    "#ffa500": "orange",
}

CHAPTER_QUIZ_DURATION = {
    300: "5 min",
    420: "7 min",
    600: "10 min",
    780: "13 min",
    900: "15 min",
    1020: "17 min",
    1200: "20 min",

}


# Create your models here.
class Grade(models.Model):
    name = models.CharField(max_length=50, unique=True)
    grade_slug = models.CharField(max_length=1000, null=True, blank=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.grade_slug:
            self.grade_slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher")
    grade = models.ForeignKey(
        "Grade", on_delete=models.CASCADE, related_name="teachers", default=0
    )

    def __str__(self):
        return (
            self.user.first_name
            + " "
            + self.user.last_name
            + " - ("
            + self.user.username
            + ")"
        )


class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="students")
    student_slug = models.CharField(max_length=70, null=True, blank=True)
    color = models.CharField(
        max_length=20, choices=tuple(COLORS.items()), default="blue"
    )

    def save(self, *args, **kwargs):
        if not self.student_slug:
            self.student_slug = slugify(self.first_name)
        return super().save(*args, **kwargs)


class Subject(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="subjects")
    name = models.CharField(max_length=50)
    subject_slug = models.CharField(
        max_length=1000,
        null=True,
        blank=True,
    )
    description = models.CharField(default="", max_length=200, null=True, blank=True)
    thumbnail = models.ImageField(upload_to="learn/subject/thumbnails")

    def save(self, *args, **kwargs):
        if not self.subject_slug:
            self.subject_slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.thumbnail.delete()
        return super().delete(*args, **kwargs)

    def __str__(self):
        return self.name + " - " + self.grade.name


class Topic(models.Model):
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="topics"
    )
    name = models.CharField(max_length=50)
    topic_slug = models.CharField(max_length=1000, null=True, blank=True)
    description = models.CharField(default="", max_length=200, null=True, blank=True)
    thumbnail = models.ImageField(upload_to="learn/topic/thumbnails")
    review = models.CharField(default="", max_length=600, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.topic_slug:
            self.topic_slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.thumbnail.delete()
        return super().delete(*args, **kwargs)

    def __str__(self):
        return self.name + " - " + self.subject.name + " - " + self.subject.grade.name


class Chapter(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="chapters")
    name = models.CharField(max_length=50)
    number = models.IntegerField(unique=True)
    chapter_slug = models.CharField(max_length=1000, null=True, blank=True)
    description = models.CharField(default="", max_length=200, null=True, blank=True)
    thumbnail = models.ImageField(upload_to="learn/chapter/thumbnails")
    review = models.CharField(default="", max_length=600, null=True, blank=True)
    content = models.TextField()

    def save(self, *args, **kwargs):
        if not self.chapter_slug:
            self.chapter_slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.thumbnail.delete()
        return super().delete(*args, **kwargs)


class StudentChapterCompletion(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    date_completed = models.DateTimeField(null=True, blank=True)


class Quotes(models.Model):
    quote = models.CharField(max_length=500)
    author = models.CharField(max_length=50, null=True, blank=True)




# CHAPTER QUIZ
class ChapterQuiz(models.Model):
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, related_name="questions"
    )
    title = models.CharField(max_length=600)
    quiz_slug = models.CharField(max_length=1000, null=True, blank=True)
    publish = models.BooleanField(default=False)
    duration = models.IntegerField(null=True, blank=True, choices=tuple(CHAPTER_QUIZ_DURATION.items()), default="5 min")
    time_start = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.quiz_slug:
            self.quiz_slug = slugify(self.title)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Chapter Quizzes"


class ChapterQuestion(models.Model):
    question_text = models.CharField(max_length=200)
    quiz = models.ForeignKey(
        ChapterQuiz, on_delete=models.CASCADE, related_name="questions"
    )

    def __str__(self):
        return self.question_text


class ChapterChoice(models.Model):
    question = models.ForeignKey(
        ChapterQuestion, on_delete=models.CASCADE, related_name="choices"
    )
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    explanation = models.CharField(default="", max_length=200, null=True, blank=True)
    mark = models.IntegerField(default=1)

    def __str__(self):
        return self.choice_text


class ChapterStudentResponse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(ChapterQuestion, on_delete=models.CASCADE)
    quiz = models.ForeignKey(ChapterQuiz, on_delete=models.CASCADE)
    choice = models.ForeignKey(ChapterChoice, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student.first_name} - {self.question.question_text}"
    
    def calculate_marks(self):
        total_marks = sum(
            choice.mark for choice in self.question.choices.all() #if choice.is_correct
        )
        return total_marks   


# End Line
