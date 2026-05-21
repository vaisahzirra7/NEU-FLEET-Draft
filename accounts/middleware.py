from django.shortcuts import redirect
from django.conf import settings

CHANGE_PASSWORD_URL = "/auth/change-password/"


class LoginRequiredMiddleware:
    """
    1. Redirects unauthenticated users to login.
    2. Forces users with must_change_password=True to the change-password
       page before they can access anything else.
    """
    EXEMPT = {
        settings.LOGIN_URL,
        "/auth/login/",
        CHANGE_PASSWORD_URL,
        "/auth/forgot-password/",
        "/auth/forgot-password/verify/",
        "/auth/forgot-password/confirm/",
    }

    # Path prefixes that bypass auth (variable URL segments like invite tokens).
    EXEMPT_PREFIXES = (
        "/auth/invite/",
        "/media/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info

        if path.startswith("/static/"):
            return self.get_response(request)

        if not request.user.is_authenticated:
            if path not in self.EXEMPT and not any(path.startswith(p) for p in self.EXEMPT_PREFIXES):
                return redirect(f"{settings.LOGIN_URL}?next={path}")
            return self.get_response(request)

        # Force password change
        if (
            getattr(request.user, "must_change_password", False)
            and path not in self.EXEMPT
            and not any(path.startswith(p) for p in self.EXEMPT_PREFIXES)
        ):
            return redirect(CHANGE_PASSWORD_URL)

        return self.get_response(request)
