class TokenInfo:
    def __init__(self, client_id=None, scope=None, expires_in=None, user=None):
        self.client_id = client_id
        self.scope = scope or []
        self.expires_in = expires_in
        self.user = user

    def to_dict(self):
        return {
            "client_id": self.client_id,
            "scope": self.scope,
            "expires_in": self.expires_in,
            "user": self.user.to_dict() if self.user else None,
        }

class UserInfo:
    def __init__(self, id=None, email=None, display_name=None):
        self.id = id
        self.email = email
        self.display_name = display_name

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "display_name": self.display_name,
        }


