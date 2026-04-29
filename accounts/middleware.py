from django.shortcuts import redirect
from django.conf import settings


class LoginRequiredMiddleware:
    """
    Redirects unauthenticated users to login for every URL
    except those in EXEMPT_URLS (login page itself).
    This means we don't need @login_required on every view.
    """
    EXEMPT = {
        settings.LOGIN_URL,
        "/auth/login/",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            path = request.path_info
            if path not in self.EXEMPT and not path.startswith("/static/"):
                return redirect(f"{settings.LOGIN_URL}?next={path}")
        return self.get_response(request)
