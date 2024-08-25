from django.contrib.auth.models import AnonymousUser

from users.authentication import JWTAuthentication


class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self._exclusion_list = ("/register", "/login")

    def __call__(self, request):
        if request.path not in self._exclusion_list and not request.path.startswith(
            "/admin/"
        ):
            user_auth_tuple = JWTAuthentication().authenticate(request)
            if user_auth_tuple:
                request.user = user_auth_tuple[0]
            else:
                request.user = AnonymousUser()
        return self.get_response(request)
