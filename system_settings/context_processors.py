from .models import SystemSettings


def branding(request):
    """
    Inject system branding into every template's context.

    Returns a single key 'brand' (a SystemSettings instance). Templates use:
      {{ brand.institution_name }}
      {{ brand.institution_subtitle }}
      {{ brand.system_name }}
      {{ brand.logo_url }}   <- None if no logo uploaded
      {{ brand.favicon_url }} <- None if no favicon uploaded
      {{ brand.email_from }}

    Performance: SystemSettings is a single-row table. The .get() call is one
    indexed lookup per request. Caching can be added later if needed.
    """
    try:
        return {"brand": SystemSettings.get()}
    except Exception:
        # During initial migration or if DB is unavailable, fail gracefully
        # so the login page can still render. Return a stub object with the
        # default values.
        class _Stub:
            system_name          = SystemSettings.SYSTEM_NAME_DEFAULT
            institution_name     = SystemSettings.INST_NAME_DEFAULT
            institution_subtitle = SystemSettings.INST_SUBTITLE_DEFAULT
            email_from           = SystemSettings.EMAIL_FROM_DEFAULT
            logo_url             = None
            favicon_url          = None
        return {"brand": _Stub()}
