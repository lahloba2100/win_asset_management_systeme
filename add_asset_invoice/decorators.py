from functools import wraps
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required



class HasPermission:
    def __init__(self, permission):
        self.permission = permission

    def __call__(self, view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # قم بفحص وجود الصلاحية هنا
            user = request.user
            if user.userpermission_set.filter(permission=self.permission).exists():
                return view_func(request, *args, **kwargs)
            else:
                # إذا لم يكن لديه الصلاحيات، قم بتوجيهه إلى صفحة permission-denied
                return HttpResponseRedirect(reverse('permission-denied'))

        return _wrapped_view
    

