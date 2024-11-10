import gradio as gr
import requests

# API endpoint URL
API_URL = "http://localhost:8000/chat/"  # Replace with your FastAPI backend URL

# Function to process chat messages
def chat_with_backend(user_id, user_message, chat_history):
    if not user_message.strip():
        return chat_history + [("User", user_message), ("Assistant", "Please enter a valid message.")]

    # Prepare payload for the backend
    payload = {"user_id": user_id, "message": user_message}
    try:
        response = requests.post(API_URL, json=payload)

        if response.status_code == 200:
            assistant_message = response.json().get("response", "No response received.")
        else:
            assistant_message = f"Error {response.status_code}: {response.text}"
    except requests.exceptions.RequestException as e:
        assistant_message = f"Error connecting to the backend: {str(e)}"

    # Update chat history
    chat_history.append(("User", user_message))
    chat_history.append(("Assistant", assistant_message))
    return chat_history

# Gradio Interface
def chatbot_interface(user_id, user_message, chat_history=[]):
    chat_history = chat_with_backend(user_id, user_message, chat_history)
    return "", chat_history  # Clear input field after sending

# Gradio App Layout
with gr.Blocks() as chat_app:
    gr.Markdown("## Itinerary Planner Chat Interface")

    with gr.Row():
        user_id = gr.Textbox(label="User ID", value="user123", placeholder="Enter your unique User ID")

    chat_history = gr.Chatbot()
    user_message = gr.Textbox(
        label="Your Message",
        placeholder="Type your message here and press Enter",
        lines=1,
        interactive=True
    )
    send_button = gr.Button("Send")

    # Link the inputs and outputs
    user_message.submit(chatbot_interface, inputs=[user_id, user_message, chat_history], outputs=[user_message, chat_history])
    send_button.click(chatbot_interface, inputs=[user_id, user_message, chat_history], outputs=[user_message, chat_history])

# Launch the app
if __name__ == "__main__":
    chat_app.launch(server_name="0.0.0.0", server_port=7860)
