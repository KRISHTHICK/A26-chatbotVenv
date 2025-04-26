import streamlit as st
import requests
import json

# Streamlit UI setup
st.title("Simple Chatbot with Ollama")
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Input for the Ollama model name.  Make this a selectbox.
model_name = st.sidebar.selectbox(
    "Choose an Ollama model:",
    ["mistral", "llama2", "codellama"],  # Add more models as they become available
    index=0,  # Default to the first model in the list
)
# System prompt
system_prompt = st.sidebar.text_area(
    "System Prompt (Optional):",
    "You are a helpful assistant.",
    help="Customize the bot's behavior with a system prompt.",
)

ollama_url = "http://localhost:11434/api/chat"  # Default Ollama API endpoint

def send_message_to_ollama(message, model=model_name, system_prompt_input=system_prompt):
    """
    Sends a message to the Ollama API and returns the response.

    Args:
        message (str): The user's message.
        model (str, optional): The Ollama model to use. Defaults to "mistral".
        system_prompt_input (str, optional): The system prompt. Defaults to "You are a helpful assistant.".

    Returns:
        str: The model's response, or None on error.
    """
    try:
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt_input},
                {"role": "user", "content": message},
            ],
            "stream": False,  # Get the full response at once for simplicity
        }
        response = requests.post(ollama_url, json=data)

        if response.status_code == 200:
            result = response.json()
            # Extract the response.  Handles possible errors in the response structure.
            if 'message' in result and 'content' in result['message']:
                return result["message"]["content"]
            else:
                return "Error: Unexpected response structure from Ollama."
        else:
            return f"Error: Ollama API request failed with status code {response.status_code} and text: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to connect to Ollama API: {e}"
    except json.JSONDecodeError as e:
        return f"Error: Failed to decode JSON response from Ollama: {e}.  Response text: {response.text}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is your question?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get the response from Ollama
    response = send_message_to_ollama(prompt)

    # Display the response
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant message to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
