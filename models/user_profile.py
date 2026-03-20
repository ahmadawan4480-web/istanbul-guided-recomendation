from database.db_connection import DatabaseConnection
import statistics

class UserProfile:
    def __init__(self, user_id, name=None, interests=None):
        self.db = DatabaseConnection()
        self.user_id = user_id
        self.name = name
        self.interests = interests or []

        # Load from database if exists
        user_data = self.db.get_user(user_id)
        if user_data:
            self.name = user_data['name']
            self.interests = user_data['interests']
        elif name:  # Create new user
            self.db.create_user(user_id, name, interests)

    def update_interests(self, new_interests):
        self.interests = new_interests
        self.db.update_user_interests(self.user_id, new_interests)

    def get_interests(self):
        return self.interests

    def add_rating(self, place_name, rating):
        """Add a rating for a place (1-5)"""
        if 1 <= rating <= 5:
            self.db.add_rating(self.user_id, place_name, rating)
            return True
        return False

    def get_ratings(self):
        """Get all user ratings"""
        return self.db.get_user_ratings(self.user_id)

    def get_average_rating(self):
        """Calculate average rating given by user"""
        ratings = self.get_ratings()
        if not ratings:
            return 0.0
        scores = [r['rating'] for r in ratings]
        return round(statistics.mean(scores), 2)

    def mark_visited(self, place_name):
        """Mark a place as visited"""
        self.db.add_visited_place(self.user_id, place_name)

    def get_visited_places(self):
        """Get list of visited places"""
        return self.db.get_visited_places(self.user_id)

    def get_profile_summary(self):
        """Get complete profile summary"""
        ratings = self.get_ratings()
        visited = self.get_visited_places()

        return {
            'user_id': self.user_id,
            'name': self.name,
            'interests': self.interests,
            'total_ratings': len(ratings),
            'average_rating_given': self.get_average_rating(),
            'visited_places': len(visited),
            'recent_ratings': ratings[-5:] if ratings else [],  # Last 5 ratings
            'recent_visits': visited[-5:] if visited else []   # Last 5 visits
        }