# asset_management/middleware.py

'''from django.contrib.auth import logout

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # التحقق من حالة المستخدم وانتهاء مؤقت الجلسة
        if request.user.is_authenticated and request.session.get_expire_at_browser_close():
            # تسجيل الخروج إذا كانت الجلسة انتهت
            logout(request)

        return response'''
'''from django.shortcuts import redirect

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and not request.path_info == '/login/':
            return redirect('/login/')  # إعادة توجيه إلى صفحة تسجيل الدخول إذا لم يتم تسجيل الدخول
        response = self.get_response(request)
        return response'''
