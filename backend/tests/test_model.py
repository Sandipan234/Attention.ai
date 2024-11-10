from backend.models.LLM import chat_with_model, extract_preferences

# Example user preferences
user_preferences = {
    "historical": "high",
    "food": "moderate",
    "activity": "adventurous"
}

# User's input for the model
prompt = """
You are a helpful assistant. The user has the following preferences:
- Budget: average
- Location: Rome
- Preferences: historical (high), food (moderate)

Based on the user's preferences and the new input, suggest an updated itinerary.

User Input: What should I do today in Rome?
"""

# Call the function
# response = chat_with_model(prompt)
# print("LLM Response:", response)

user_input = "I enjoy historical places in Delhi and love food. My budget is comfortable."

preferences = extract_preferences(user_input)
print(preferences)

{
    "user_id": "test_user",
    "message": "try the local cuisine"
}