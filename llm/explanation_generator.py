import openai
import os
import hashlib
import random
from database.db_connection import DatabaseConnection

# Set your OpenAI API key here
api_key = os.getenv("OPENAI_API_KEY")  # Or set directly: "your-api-key"

def get_cache_key(item, interests):
    """Generate a unique cache key for LLM responses"""
    key_data = f"{item['name']}_{item['category']}_{'_'.join(sorted(interests))}"
    return hashlib.md5(key_data.encode()).hexdigest()

def generate_ai_explanation(item, interests):
    """Generate sophisticated AI-like explanations without API dependency"""
    name = item['name']
    category = item['category']

    # Pre-defined explanation templates for different categories and interests
    templates = {
        'historical': {
            'history': [
                f"As someone passionate about history, you'll be captivated by {name}, a magnificent {category} site that has witnessed centuries of Istanbul's rich heritage. This architectural marvel offers a fascinating glimpse into the city's Byzantine and Ottoman past, with intricate details that bring history to life.",
                f"Your interest in history makes {name} a perfect match! This stunning {category} landmark stands as a testament to Istanbul's glorious past, featuring remarkable preservation of ancient architectural elements and historical significance that will transport you through time.",
                f"For history enthusiasts, {name} represents the pinnacle of Istanbul's {category} treasures. Discover the fascinating stories embedded in its ancient stones and learn about the pivotal role this site played in shaping the city's cultural identity."
            ],
            'architecture': [
                f"Your appreciation for architecture will be delighted by {name}, showcasing masterful {category} design that exemplifies Istanbul's architectural evolution. The intricate craftsmanship and structural elegance make this a must-visit destination for architectural enthusiasts.",
                f"As an architecture lover, {name} offers a perfect study in {category} excellence. Marvel at the sophisticated design elements and construction techniques that have made this site an enduring symbol of architectural achievement in Istanbul."
            ],
            'culture': [
                f"Your interest in culture aligns perfectly with {name}, a premier {category} destination that embodies Istanbul's rich cultural tapestry. Experience the harmonious blend of different civilizations that have shaped this remarkable site over centuries.",
                f"For those fascinated by cultural heritage, {name} provides an immersive journey through Istanbul's {category} legacy. Discover how this site reflects the city's role as a cultural crossroads between East and West."
            ]
        },
        'religious': {
            'religion': [
                f"Your spiritual interests will be enriched by {name}, a sacred {category} site that represents the pinnacle of Ottoman architectural and spiritual achievement. The serene atmosphere and magnificent design create a deeply moving religious experience.",
                f"As someone interested in religious sites, {name} offers a profound spiritual journey through Islamic art and architecture. The harmonious blend of functionality and beauty makes this mosque a masterpiece of religious design."
            ],
            'architecture': [
                f"Your architectural interests will be captivated by {name}, where {category} design reaches extraordinary heights. The perfect proportions, intricate tile work, and soaring domes create a breathtaking display of architectural mastery.",
                f"For architecture enthusiasts, {name} exemplifies the finest in {category} design. The masterful integration of form and function, combined with exquisite decorative elements, makes this a landmark of architectural excellence."
            ],
            'history': [
                f"Your historical interests will be served well at {name}, a {category} site that has played a central role in Istanbul's religious and cultural history. Discover the fascinating evolution of this sacred space through different eras.",
                f"History buffs will appreciate {name} as a living testament to Istanbul's {category} heritage. The site's historical significance spans centuries, offering insights into the city's religious and cultural development."
            ]
        },
        'nature': {
            'nature': [
                f"Your love for nature will be fulfilled at {name}, where Istanbul's natural beauty shines through. This scenic {category} destination offers a peaceful retreat amidst the city's urban landscape, perfect for relaxation and rejuvenation.",
                f"As a nature enthusiast, you'll find {name} to be a delightful escape in Istanbul. The tranquil setting and natural surroundings provide a refreshing contrast to the city's bustling energy."
            ],
            'scenic': [
                f"For those who appreciate scenic beauty, {name} delivers breathtaking views and a memorable {category} experience. The stunning vistas and peaceful atmosphere make this an ideal spot for contemplation and photography.",
                f"Your interest in scenic locations makes {name} an excellent choice. This {category} gem offers panoramic views and a serene environment that captures the essence of Istanbul's natural charm."
            ]
        },
        'food': {
            'food': [
                f"Your culinary interests will be delighted by {name}, a premier destination for experiencing Istanbul's rich gastronomic heritage. This {category} establishment offers authentic flavors and traditional dishes that showcase the city's diverse food culture.",
                f"As a food lover, {name} promises an unforgettable culinary journey through Istanbul's {category} scene. Discover the authentic tastes and traditional cooking methods that have made this city famous for its cuisine."
            ],
            'culture': [
                f"Your cultural interests align perfectly with {name}, where {category} traditions come alive through food. Experience the social aspect of dining and learn about Istanbul's culinary customs that bring people together.",
                f"For those interested in cultural experiences, {name} offers more than just food—it's a window into Istanbul's {category} traditions and social customs that have evolved over generations."
            ]
        }
    }

    # Find matching interests
    matching_interests = [interest for interest in interests if interest in templates.get(category, {})]

    if not matching_interests:
        # Fallback to general interest
        primary_interest = interests[0] if interests else 'exploration'
        explanation = f"Based on your interest in {primary_interest}, {name} offers a unique {category} experience in Istanbul that combines cultural significance with memorable attractions."
    else:
        # Use a random template from matching interests
        primary_interest = random.choice(matching_interests)
        category_templates = templates[category][primary_interest]
        explanation = random.choice(category_templates)

    return explanation

def generate_explanation(item, interests):
    # Check cache first
    db = DatabaseConnection()
    cache_key = get_cache_key(item, interests)
    cached_response = db.get_cached_llm_response(cache_key)

    if cached_response:
        return cached_response

    if not api_key:
        # Use sophisticated AI-like explanations without API
        explanation = generate_ai_explanation(item, interests)
    else:
        client = openai.OpenAI(api_key=api_key)

        prompt = f"Generate a contextual explanation for recommending {item['name']}, a {item['category']} in Istanbul, to a user interested in {', '.join(interests)}. Make it engaging and informative, highlighting why it matches their interests. Keep it to 2-3 sentences and make it sound natural and conversational."

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a knowledgeable and engaging travel assistant specializing in Istanbul recommendations. Provide personalized, insightful explanations that highlight unique aspects of each location."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            explanation = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating explanation: {e}")
            explanation = generate_ai_explanation(item, interests)

    # Cache the response (TTL: 24 hours for better variety)
    db.cache_llm_response(cache_key, explanation, ttl=86400)

    return explanation