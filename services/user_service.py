from django.contrib.auth import get_user_model

User = get_user_model()


class UserService:
    def validate_user_credentials(self, email, password):
        user = User.objects.filter(email=email).first()
        if not user:
            raise ValueError("User does not exist")
        if not user.check_password(password):
            raise ValueError("Incorrect password")
        return user

    def create_user(self, username, email, first_name, last_name, password):
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        return user
