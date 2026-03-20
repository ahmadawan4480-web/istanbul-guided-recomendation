import pytest
from recommendation.recommender import recommend_items, cosine_similarity, create_vector
from models.user_profile import UserProfile
from database.db_connection import DatabaseConnection

def test_cosine_similarity():
    """Test cosine similarity calculation"""
    vec1 = [1, 0, 1]
    vec2 = [1, 1, 0]
    similarity = cosine_similarity(vec1, vec2)
    assert similarity == 0.5  # (1*1 + 0*1 + 1*0) / (sqrt(2) * sqrt(2))

def test_create_vector():
    """Test vector creation from terms"""
    terms = ['history', 'culture', 'food']
    interests = ['history', 'food']
    vector = create_vector(interests, terms)
    assert vector == [1, 0, 1]

def test_recommend_items():
    """Test recommendation system"""
    interests = ['history', 'culture']
    recommendations = recommend_items(interests, limit=3)

    assert len(recommendations) <= 3
    assert all('hybrid_score' in rec for rec in recommendations)
    assert all(rec['hybrid_score'] >= 0 for rec in recommendations)

def test_user_profile():
    """Test user profile creation and management"""
    profile = UserProfile('test_user', 'Test User', ['history'])

    assert profile.user_id == 'test_user'
    assert profile.name == 'Test User'
    assert 'history' in profile.get_interests()

    # Test rating
    success = profile.add_rating('Hagia Sophia', 5)
    assert success

    ratings = profile.get_ratings()
    assert len(ratings) == 1
    assert ratings[0]['place_name'] == 'Hagia Sophia'
    assert ratings[0]['rating'] == 5

def test_database_operations():
    """Test database operations"""
    db = DatabaseConnection()

    # Create test user
    db.create_user('test_db_user', 'Test DB User', ['test'])

    # Retrieve user
    user = db.get_user('test_db_user')
    assert user is not None
    assert user['name'] == 'Test DB User'

    # Add rating
    db.add_rating('test_db_user', 'Test Place', 4.5)

    # Get ratings
    ratings = db.get_user_ratings('test_db_user')
    assert len(ratings) == 1
    assert ratings[0]['place_name'] == 'Test Place'

if __name__ == "__main__":
    pytest.main([__file__])