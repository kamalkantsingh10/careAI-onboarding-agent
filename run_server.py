from flask import Flask, request, jsonify
import requests
import os
import json
from dotenv import load_dotenv
from tinydb import TinyDB
from framework.handlers import call_ended, function_call,tool_call,onboarding_call_ended
from framework.functions import call_function

load_dotenv()  # Load environment variables from .env file


app = Flask(__name__)
  # store securely

db_customer=TinyDB("db/customers.json")
db_conversation=TinyDB("db/conversations.json")



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
def tool_call():
    all_responses = []
    print("in tool call")
    event = request.json
    #executed when a tool is called
    with open('test.json', 'w') as f: json.dump(event, f, indent=2)
    
    payload = event.get("message", {})
    event_type = payload.get("type")
    tool_name = payload.get("name")
    call_id = payload.get("call").get("id")
    tool_calls= payload.get("toolCalls")
    
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





app.run(port=5000)