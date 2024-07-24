# middleware.py
from django.utils import timezone
from django.shortcuts import redirect
from django.urls import reverse


class TimerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return self.process_timer(request, response)

    def process_timer(self, request, response):
        if request.resolver_match.view_name == "chapter_quiz_content":
            student_slug = request.resolver_match.kwargs.get("student_slug")
            subject_slug = request.resolver_match.kwargs.get("subject_slug")
            topic_slug = request.resolver_match.kwargs.get("topic_slug")
            chapter_slug = request.resolver_match.kwargs.get("chapter_slug")
            quiz_slug = request.resolver_match.kwargs.get("quiz_slug")

            if "timer_start" not in request.session:
                request.session["timer_start"] = timezone.now().timestamp()
            else:
                elapsed_time = (
                    timezone.now().timestamp() - request.session["timer_start"]
                )
                if elapsed_time >= 300:  # 300 seconds (5 minutes)
                    redirect_url = reverse(
                        "index_learn"
                    )  # Replace 'index' with the name of your index view
                    return redirect(redirect_url)

        return response
