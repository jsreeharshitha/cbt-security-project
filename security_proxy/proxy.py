from fastapi import FastAPI, Header, HTTPException, Request
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI(title="Telecom-CAMARA API Security Proxy - Governor")

# ====== Key Generation (For Sandbox Testing) ======
# In production: 
# The Public Key is fetched from an Auth Server/JWKS.
# The Private Key stays secured on the Agent's hardware.
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()
pem_public_key = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

class ActionRequest(BaseModel):
    user_intent: str
    api_action: str

# ====== LAYER 2: INTENTGUARD KNOWLEDGE BASE (Simulated Vector DB) ======
# In production, this would be a ChromaDB/Pinecone instance.
AUTHORIZED_INTENTS = {
    "SIM_SWAP": [
        "check if my sim was changed",
        "verify sim card swap status",
        "did someone change my sim recently",
        "check sim fraud"
    ],
    "DEVICE_LOCATION": [
        "where is my phone",
        "get device coordinates",
        "track my mobile location",
        "find my device"
    ],
    "CONNECTIVITY": [
        "is my device online",
        "check network attachment status",
        "verify 5g connection status"
    ]
}

def analyze_intent(user_input: str, requested_api: str, threshold: float = 0.15) -> dict:
    """
    Calculates semantic distance (Cosine Similarity) between the user's prompt 
    and the authorized intents for the requested CAMARA API.
    """
    if requested_api not in AUTHORIZED_INTENTS:
        return {"aligned": False, "score": 0.0, "reason": "Unknown API Action."}
    allowed_phrases = AUTHORIZED_INTENTS[requested_api]    
    corpus = [user_input.lower()] + allowed_phrases
    try:
        vectorizer = TfidfVectorizer().fit_transform(corpus)
        vectors = vectorizer.toarray()
        user_vector = vectors[0].reshape(1, -1)
        allowed_vectors = vectors[1:]
        similarities = cosine_similarity(user_vector, allowed_vectors)
        max_score = float(similarities.max())
        if max_score >= threshold:
            return {"aligned": True, "score": max_score, "reason": "Intent semantically aligned."}
        else:
            return {"aligned": False, "score": max_score, "reason": "Semantic mismatch. Possible Prompt Injection."}
            
    except Exception as e:
         return {"aligned": False, "score": 0.0, "reason": f"Vectorization error: {str(e)}"}

# ====== LAYER 3: DEVICE CONTEXT DATABASE (Mock Network State) ======
# In production, this data comes from the 5G Core Network (NWDAF or PCF)
DEVICE_CONTEXT_DB = {
    "gemma3-agent-001": {
        "network_slice": "Secure_5G_Management",
        "roaming_status": False,
        "threat_level": "Low"
    },
    "compromised-agent-999": {
        "network_slice": "Public_WiFi",
        "roaming_status": True,
        "threat_level": "High"
    }
}

def validate_context(agent_id: str, requested_api: str) -> dict:
    """Checks if the agent's real-time network context allows the requested API."""
    context = DEVICE_CONTEXT_DB.get(agent_id)
    if not context:
        return {"allowed": False, "reason": "Agent context not found in network core."}
    
    # Strict Policy: SIM_SWAP requires a Secure slice and no roaming.
    if requested_api == "SIM_SWAP":
        if context["network_slice"] != "Secure_5G_Management":
            return {"allowed": False, "reason": f"Context Violation: On insecure slice ({context['network_slice']})."}
        if context["roaming_status"]:
            return {"allowed": False, "reason": "Context Violation: Cannot execute SIM_SWAP while roaming."}            
    return {"allowed": True, "reason": "Context policies passed."}
    
# ====== Security Proxy Pipeline Layers: 1,2,3 ======
@app.post("/validate-action")
async def validate_action(
    request: ActionRequest, 
    x_dpop_proof: str = Header(None, alias="X-DPoP-Proof")
):
    print(f"--- Intercepted Request: {request.api_action} ---")

    # ====== LAYER 1: DPoP AUTH CHECK ======
    if not x_dpop_proof:
        raise HTTPException(status_code=401, detail="Missing DPoP Proof. Request Blocked.")
    try:
        # Verify the JWT signature using the Agent's Public Key
        decoded_token = jwt.decode(
            x_dpop_proof, 
            pem_public_key, 
            algorithms=["RS256"],
            options={"verify_aud": False} # Skipping audience check for local sandbox
        )
        print("DPoP Signature Verified. Token belongs to this Agent.")
        print(f"[LAYER 1] Checking DPoP Proof for Agent ID: {decoded_token.get('sub', 'Unknown')}")
        print(f"[LAYER 1] Bound to Public Key Thumbprint: ...{str(pem_public_key)[-20:]}")
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="DPoP Token Expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid DPoP Signature. Stolen Token Detected!")

    # ====== LAYER 2: INTENTGUARD ANALYSIS (Semantic) ======
    print(f"\n[LAYER 2] Analyzing Semantic Intent...")
    print(f"   User Prompt: '{request.user_intent}'")
    print(f"   Requested Action: '{request.api_action}'")
    intent_result = analyze_intent(request.user_intent, request.api_action)
    print(f"   Semantic Score: {intent_result['score']:.4f} (Threshold: 0.15)")
    if not intent_result["aligned"]:
        print(f"Layer 2 FAILED: {intent_result['reason']}")
        raise HTTPException(
            status_code=403, 
            detail=f"IntentGuard Blocked Request: {intent_result['reason']}"
        )
    print("Layer 2 Passed: Action aligns with user intent.")

# ====== LAYER 3: CONTEXT BINDING (Session-Aware) ======
# Extracting the agent_id from the token we decoded in Layer 1
    agent_id = decoded_token.get("sub", "Unknown")    
    print(f"\n[LAYER 3] Evaluating Network Context for Agent: {agent_id}...")
    context_result = validate_context(agent_id, request.api_action)    
    if not context_result["allowed"]:
        print(f"Layer 3 FAILED: {context_result['reason']}")
        raise HTTPException(
            status_code=403, 
            detail=f"Context Binding Blocked: {context_result['reason']}"
        )        
    print("Layer 3 Passed: Device context meets strict security policies.")
    print("\n ALL 3 ZERO-TRUST LAYERS PASSED. Forwarding to CAMARA API...") 
    return {
        "status": "authorized",
        "message": f"Action {request.api_action} verified by all 3 layers of Security Proxy.",
        "forward_to": "CAMARA_API_GATEWAY"
    }

# ====== Helper Endpoint for Testing ======
@app.get("/generate-test-token/{agent_id}")
def generate_test_token(agent_id: str):
    """Generates a valid signed token using the sandbox private key for testing."""
    pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    token = jwt.encode({"sub": agent_id, "test": "data"}, pem_private_key, algorithm="RS256")
    return {"token": token}