from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

RULES_FILE = "D:\Desktop\Vedixxxxx\IAI Chatbot\legalaid.json"

def load_legal_rules():
    try:
        if os.path.exists(RULES_FILE):
            with open(RULES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("rules", [])
        else:
            print(f"Error: {RULES_FILE} file not found!")
            return []
    except Exception as e:
        print(f"Error loading legal rules file: {e}")
        return []

legal_rules = load_legal_rules()

greetings = ["hi", "hello", "hey", "start", "help"]
closings = ["bye", "goodbye", "exit", "quit", "thank you", "thanks"]

INITIAL_BOT_GREETING = "Hello! I'm your Legal Expert Assistant. How can I help you today?"

def find_matching_rule(user_input):
    user_input_lower = user_input.lower()
    
    for rule in legal_rules:
        keywords = rule.get("keywords", [])
        for keyword in keywords:
            if keyword.lower() in user_input_lower:
                return rule.get("answer", "Sorry, no answer available for this topic.")
    
    return None

def get_response(user_input):
    user_input_lower = user_input.lower().strip()
    
    if not user_input_lower:
        return INITIAL_BOT_GREETING, False
    
    if any(greet in user_input_lower for greet in greetings):
        return "Hi! What legal question can I help you with today?", False

    if any(close in user_input_lower for close in closings):
        return "Thank you for using the Legal Assistant. Have a great day!", True

    legal_answer = find_matching_rule(user_input)
    if legal_answer:
        return legal_answer, False

    return "I'm sorry, I couldn't find information about that legal topic. Please try asking about specific legal concepts, acts, or procedures.", False

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Legal Aid Chatbot API is running!",
        "endpoints": {
            "chat": "/chat (POST)",
            "status": "/status (GET)"
        }
    })

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "status": "running",
        "rules_loaded": len(legal_rules),
        "file_path": RULES_FILE,
        "file_exists": os.path.exists(RULES_FILE)
    })

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        user_message = data.get("message", "").strip()
        
        if not user_message:
            return jsonify({
                "response": INITIAL_BOT_GREETING, 
                "conversation_ended": False
            })
        
        response, ended = get_response(user_message)
        
        return jsonify({
            "response": response,
            "conversation_ended": ended,
            "user_input": user_message
        })
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    print(f"Loading legal rules from: {RULES_FILE}")
    print(f"Loaded {len(legal_rules)} legal rules")
    print("Starting Legal Aid Chatbot server...")
    print("API Endpoints:")
    print("  GET  /        - Home page")
    print("  GET  /status  - Check status")
    print("  POST /chat    - Chat with bot")
    
    app.run(debug=True, host='0.0.0.0', port=5000)