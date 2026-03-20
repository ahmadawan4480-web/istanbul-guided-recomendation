import openai
import os

# Set your OpenAI API key here
openai.api_key = os.getenv("OPENAI_API_KEY")  # Or set directly: "your-api-key"

def generate_explanation(item, interests):
    if not openai.api_key:
        # Fallback to simple template if no API key
        return f"This {item['category']} is recommended because you are interested in {', '.join(interests)}. {item['name']} offers a unique experience in Istanbul."

    prompt = f"Generate a contextual explanation for recommending {item['name']}, a {item['category']} in Istanbul, to a user interested in {', '.join(interests)}. Make it engaging and informative, highlighting why it matches their interests."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for travel recommendations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        explanation = response.choices[0].message.content.strip()
        return explanation
    except Exception as e:
        print(f"Error generating explanation: {e}")
        return f"This {item['category']} is recommended because you are interested in {', '.join(interests)}. {item['name']} offers a unique experience in Istanbul."