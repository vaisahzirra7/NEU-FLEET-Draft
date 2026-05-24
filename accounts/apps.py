from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'
    default = True

    def ready(self):
        # Import signal handlers to register them.
        from . import signals  # noqa: F401
