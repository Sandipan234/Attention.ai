from backend.utils.neo4j_service import DynamicPreferenceUpdater

# Initialize the service
db_service = DynamicPreferenceUpdater(uri="bolt://localhost:7687", user="neo4j", password="#Sandipan55")

# Save user preferences with contexts

# Save user preferences with context
db_service.save_user_data_with_context(
    user_id="user123",
    location="Delhi",
    preferences=[{"type": "food", "intensity": "high"}]
)

db_service.save_user_data_with_context(
    user_id="user123",
    location=None,  # This will automatically use the latest valid location
    preferences=[{"type": "relaxation", "intensity": "moderate"}]
)

# Fetch contextual data
context_data = db_service.get_contextual_data(user_id="user123")
print("Contextual Data:", context_data)

# Fetch updated user data
final_data = db_service.get_user_data(user_id="user123")
print("Final Data:", final_data)

# Close the service
db_service.close()
