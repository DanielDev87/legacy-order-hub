from repositories.user_repository import UserRepository


class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()

    def authenticate(self, username, password):
        return self.user_repository.get_by_credentials(username, password)
