from flask import Flask, request, jsonify, render_template_string, send_from_directory
import requests
import os
import json
from dotenv import load_dotenv
from tinydb import TinyDB
from framework.handlers import call_ended, function_call, tool_call, onboarding_call_ended
from framework.functions import call_function
from data.db_manager import table_customer,table_converstaions

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

# Database setup


# Your existing webhook routes remain unchanged
@app.route("/2carehook", methods=["POST"])
def vapi_webhook():
    event = request.json
    payload = event.get("message", {})
    event_type = payload.get("type")
    print(f"📥 Received event: {event_type}")
    
    if event_type == "call_started":
        print(f"📞 Incoming call from {payload.get('from')} (ID: {payload.get('id')})")
    elif event_type == "function-call":
        function_call(event=event)
    elif event_type == "end-of-call-report":
        call_ended(event=event)
    elif event_type == "tool-calls":
        tool_call(event=event)
    elif event_type == "call_ended":
        print(f"📴 Call ended. Summary: {payload.get('summary')}")
        print("📜 Full transcript:", payload.get("transcript"))
    
    return jsonify({"status": "ok"}), 200

@app.route("/function_call", methods=["POST"])
def tool_call_route():
    all_responses = []
    print("in tool call")
    event = request.json
    
    # executed when a tool is called
    with open('test.json', 'w') as f: 
        json.dump(event, f, indent=2)
    
    payload = event.get("message", {})
    event_type = payload.get("type")
    tool_name = payload.get("name")
    call_id = payload.get("call").get("id")
    tool_calls = payload.get("toolCalls")
    
    for tool_call in tool_calls:
        tool_call_id = tool_call["id"]
        function_name = tool_call["function"]["name"]
        arguments = tool_call["function"]["arguments"]
        print(f"function: {function_name}| \n Arg {arguments}")
        
        # Call the appropriate function based on the function name
        result = call_function(function_name, arguments)
        
        # Format the response
        response = {
            "toolCallId": tool_call_id,
            "result": result
        }
        all_responses.append(response)
    
    # Combine all responses
    tool_response = {
        "results": all_responses
    }
    
    return jsonify(tool_response), 200

@app.route("/2carehook_onboarding", methods=["POST"])
def vapi_webhook_onboarding():
    event = request.json
    payload = event.get("message", {})
    event_type = payload.get("type")
    print(f"📥 Received event: {event_type}")
    
    if event_type == "call_started":
        print(f"📞 Incoming call from {payload.get('from')} (ID: {payload.get('id')})")
    elif event_type == "function-call":
        function_call(event=event)
    elif event_type == "end-of-call-report":
        onboarding_call_ended(event=event)
    elif event_type == "tool-calls":
        tool_call(event=event)
    elif event_type == "call_ended":
        print(f"📴 Call ended. Summary: {payload.get('summary')}")
        print("📜 Full transcript:", payload.get("transcript"))
    
    return jsonify({"status": "ok"}), 200

# NEW UI ROUTES BELOW
# ==================

@app.route("/")
def dashboard():
    """Serve the main dashboard UI"""
    try:
        # Read the HTML file and serve it
        with open('demo_ui/index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        # Fallback: serve embedded HTML if file doesn't exist
        return render_template_string(DASHBOARD_HTML)

@app.route("/api/customers", methods=["GET"])
def get_customers():
    """API endpoint to get all customers data"""
    try:
        # Read directly from the TinyDB database
        customers_data = table_customer.all()
        
        # If the database has a nested structure like your JSON, handle it
        if customers_data and len(customers_data) > 0:
            # Check if data is nested under 'customers' key
            first_record = customers_data[0]
            if 'customers' in first_record:
                return jsonify(first_record)
            else:
                # Data is direct, restructure it
                formatted_data = {
                    "customers": {str(i+1): customer for i, customer in enumerate(customers_data)}
                }
                return jsonify(formatted_data)
        else:
            return jsonify({"customers": {}})
            
    except Exception as e:
        print(f"Error reading customers: {e}")
        return jsonify({"error": "Failed to load customers", "customers": {}}), 500

@app.route("/api/customers/<customer_id>", methods=["GET"])
def get_customer(customer_id):
    """API endpoint to get a specific customer"""
    try:
        customers_data = table_customer.all()
        
        if customers_data and len(customers_data) > 0:
            first_record = customers_data[0]
            if 'customers' in first_record:
                customers = first_record['customers']
                if customer_id in customers:
                    return jsonify(customers[customer_id])
                else:
                    return jsonify({"error": "Customer not found"}), 404
        
        return jsonify({"error": "Customer not found"}), 404
        
    except Exception as e:
        print(f"Error reading customer: {e}")
        return jsonify({"error": "Failed to load customer"}), 500

# NEW CONVERSATIONS ENDPOINTS
# ===========================

@app.route("/api/conversations", methods=["GET"])
def get_conversations():
    """API endpoint to get all conversations data"""
    try:
        # Read directly from the TinyDB conversations database
        conversations_data = table_converstaions.all()
        
        # If the database has a nested structure, handle it
        if conversations_data and len(conversations_data) > 0:
            # Check if data is nested under 'conversations' key
            first_record = conversations_data[0]
            if 'conversations' in first_record:
                return jsonify(first_record)
            else:
                # Data is direct, restructure it
                formatted_data = {
                    "conversations": {str(i+1): conversation for i, conversation in enumerate(conversations_data)}
                }
                return jsonify(formatted_data)
        else:
            return jsonify({"conversations": {}})
            
    except Exception as e:
        print(f"Error reading conversations: {e}")
        return jsonify({"error": "Failed to load conversations", "conversations": {}}), 500

@app.route("/api/conversations/<conversation_id>", methods=["GET"])
def get_conversation(conversation_id):
    """API endpoint to get a specific conversation"""
    try:
        conversations_data = table_converstaions.all()
        
        if conversations_data and len(conversations_data) > 0:
            first_record = conversations_data[0]
            if 'conversations' in first_record:
                conversations = first_record['conversations']
                if conversation_id in conversations:
                    return jsonify(conversations[conversation_id])
                else:
                    return jsonify({"error": "Conversation not found"}), 404
        
        return jsonify({"error": "Conversation not found"}), 404
        
    except Exception as e:
        print(f"Error reading conversation: {e}")
        return jsonify({"error": "Failed to load conversation"}), 500

# Embedded HTML template as fallback
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2Care Onboarding Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .nav { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .tab-button { background: #007bff; color: white; border: none; padding: 10px 20px; margin-right: 10px; border-radius: 4px; cursor: pointer; }
        .tab-button.active { background: #0056b3; }
        .content { background: white; padding: 20px; border-radius: 8px; }
        .loading { text-align: center; padding: 40px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <button class="tab-button active">Dashboard</button>
            <button class="tab-button">Customers</button>
        </div>
        <div class="content">
            <div class="loading">Loading dashboard...</div>
            <div id="data"></div>
        </div>
    </div>
    <script>
        fetch('/api/customers')
            .then(response => response.json())
            .then(data => {
                document.querySelector('.loading').style.display = 'none';
                document.getElementById('data').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            })
            .catch(error => {
                document.querySelector('.loading').innerHTML = 'Error loading data: ' + error.message;
            });
    </script>
</body>
</html>
'''

if __name__ == "__main__":
    app.run(port=5000, debug=True)