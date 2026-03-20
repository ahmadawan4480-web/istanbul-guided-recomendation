class UserProfile:
    def __init__(self, user_id, name, interests):
        self.user_id = user_id
        self.name = name
        self.interests = interests  # list of strings

    def update_interests(self, new_interests):
        self.interests = new_interests

    def get_interests(self):
        return self.interests