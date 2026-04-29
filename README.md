# Context-bound Tokens for Securing AI Agents in Telecom Networks

## Project Overview
As AI Agents become increasingly integrated into 5G/6G telecommunication networks, providing secure access to sensitive network APIs (such as the CAMARA project) is critical. Traditional security models rely on static bearer tokens, leaving them vulnerable to token theft, LLM prompt injections, and compromised device environments. 

This project introduces a **three-layer Zero Trust Architecture Security Proxy** that shifts from perimeter defense to continuous validation. By binding access tokens to cryptographic hardware, verifying semantic intent, and evaluating dynamic network context, this proxy ensures safe and scalable execution of autonomous AI agents in next-generation telecom infrastructure.

---

## Architecture & Core Features

The security proxy implements a strict `assume breach` and defense-in-depth methodology, intercepting all requests before they reach the backend telecom APIs (e.g., SIM Swap, Device Location). 

### 1. Layer 1: Cryptographic Binding (DPoP)
Prevents traditional token theft by verifying `X-DPoP-Proof` headers. The proxy ensures the API token is mathematically bound to the physical hardware (Public Key Thumbprint) of the requesting agent.

### 2. Layer 2: Semantic IntentGuard 
Protects against LLM prompt injection and confused agent behavior. Using a mathematical `TfidfVectorizer`, the engine analyzes the natural language prompt and calculates a semantic similarity score against authorized reference sets. If the score falls below a strict safety threshold (0.15), the request is blocked.

### 3. Layer 3: Context Enforcement ("Session-Aware" Policies)
Evaluates dynamic environmental factors before granting access. The proxy checks a simulated Device Context Database to ensure the agent is operating on a secure network slice (e.g., `Secure_5G_Management`), is not on public Wi-Fi, and has a valid roaming status and SIM history. 

### Frontend Guardrails
The local LLM runtime acts as the first line of defense, intercepting direct command overrides (e.g., *"Ignore all rules..."*) and dropping malicious payloads before they transmit to the backend.

---

## Technology Stack
* **Backend Framework:** FastAPI (Python), Uvicorn
* **AI/NLP Runtime:** Ollama, Gemma3 (Local LLM Execution)
* **Mathematical Engine:** Scikit-Learn (`TfidfVectorizer`)
* **Deployment:** Docker (Containerized environments)
* **Simulated APIs:** CAMARA Network APIs (Mocked Sandbox)

---

## Setup and Installation

### Prerequisites
1. Python 3.9+
2. [Ollama](https://ollama.com/) installed locally with the Gemma3 model downloaded (`ollama run gemma3`).
3. Docker (Optional, for containerized execution).

### Local Installation
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/context-bound-tokens.git](https://github.com/yourusername/context-bound-tokens.git)
   cd context-bound-tokens
