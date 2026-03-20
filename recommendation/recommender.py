import json

# Load places dataset
def load_places():
    with open("data/places.json", "r") as file:
        places = json.load(file)
    return places

# Load events dataset
def load_events():
    with open("data/events.json", "r") as file:
        events = json.load(file)
    return events

# Recommend places and events based on user interests
def recommend_items(user_interests):
    places = load_places()
    events = load_events()
    all_items = places + events
    recommendations = []

    for item in all_items:
        score = 0
        for interest in user_interests:
            if interest in item["tags"]:
                score += 1
        if score > 0:
            recommendations.append((item, score))

    # sort by score
    recommendations.sort(key=lambda x: x[1], reverse=True)

    return [item[0] for item in recommendations]

# For backward compatibility
def recommend_places(user_interests):
    return recommend_items(user_interests)