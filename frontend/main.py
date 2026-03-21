import os
from langchain_ollama import OllamaLLM 

# Setting Ollama Environment based on Program running environment
APP_ENV = os.getenv("APP_ENV", "dev")
if APP_ENV == "prod":
    OLLAMA_URL = "http://host.docker.internal:11434"
    print("--- Running in PRODUCTION mode (Docker-to-Host) ---")
else:
    OLLAMA_URL = "http://localhost:11434"
    print("--- Running in DEVELOPMENT mode (Local-to-Local) ---")

MODEL_NAME = "gemma3:270m" 

def run_simple_agent():
    print(f"--- Connecting to Ollama at {OLLAMA_URL} ---")
    
    try:
        # Creating an LLM brain using Ollama/Gemma3 class.
        llm = OllamaLLM(model=MODEL_NAME, base_url=OLLAMA_URL)
        
        SYSTEM_PROMPT = """
            You are a specialized 5G Network Assistant for the CAMARA Project.
            Your expertise is limited to Telecom APIs: SIM Swap, Device Location, and Connectivity.
            - SIM Swap refers to checking if a phone number's SIM card was recently changed to prevent fraud.
            - If a user asks for an action, identify the required CAMARA API.
            - Keep responses technical, brief, and security-focused.
        """
        user_input = input("Enter your Prompt: ")
        print(f"User: {user_input}")
        
        # Invoke response
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_input}\nAssistant:"
        response = llm.invoke(full_prompt)
        print(f"\nGemma: {response}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Tip: If using Docker, ensure Ollama is bound to 0.0.0.0, not just 127.0.0.1")

if __name__ == "__main__":
    run_simple_agent()