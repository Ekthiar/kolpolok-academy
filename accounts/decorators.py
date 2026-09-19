from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied


def _check(role_check):
    def decorator(view_func):
        @login_required
        def wrapped(request, *args, **kwargs):
            if not role_check(request.user):
                raise PermissionDenied("এই পাতাটি দেখার অনুমতি আপনার নেই।")
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


admin_required = _check(lambda u: u.is_admin_role())
teacher_required = _check(lambda u: u.is_teacher_role() or u.is_admin_role())
student_required = _check(lambda u: u.is_student_role() or u.is_admin_role())
