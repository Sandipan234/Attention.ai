from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils.neo4j_service import DynamicPreferenceUpdater
from models.LLM import extract_preferences, chat_with_model

app = FastAPI()

# Initialize Neo4j Service
neo4j_service = DynamicPreferenceUpdater(uri="bolt://localhost:7687", user="neo4j", password="#Sandipan55")

# Define input schema for the API
class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/chat/")
async def chat_endpoint(request: ChatRequest):
    try:
        # Extract preferences and location using LLM
        user_data = neo4j_service.get_user_data(request.user_id)
        extracted_data = extract_preferences(request.message, user_data)

        if "error" in extracted_data:
            raise HTTPException(status_code=500, detail=extracted_data["error"])

        # Dynamically update user data with context-sensitive logic
        neo4j_service.save_user_data_with_context(
            user_id=request.user_id,
            location=extracted_data.get("location"),
            preferences=extracted_data.get("preferences", [])
        )

        # Generate a response using updated preferences and contextual data
        contextual_data = neo4j_service.get_contextual_data(request.user_id)
        preferences_str = ", ".join([
            f"At {item['location']}: " +
            ", ".join([f"{p['type']} ({p['intensity']})" for p in item["preferences"]])
            for item in contextual_data
        ])
        prompt = f"""
        You are a helpful assistant. The user has provided the following input:
        "{request.message}"

        Their existing preferences and locations are as follows:
        {preferences_str}

        Generate a suggestion or response specifically addressing the user's input while considering their preferences and associated locations.
        """


        llm_response = chat_with_model(prompt)
        return {"user_id": request.user_id, "response": llm_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.on_event("shutdown")
def shutdown():
    """
    Close the Neo4j connection on app shutdown.
    """
    neo4j_service.close()
