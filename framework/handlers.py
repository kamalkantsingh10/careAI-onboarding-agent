from flask import Flask, request, jsonify
import requests
import os
import json



def call_ended(event):
    #called when call is ended
    event = request.json
    payload = event.get("payload", {})
    tool_name = payload.get("name")
    call_id = payload.get("call_id")
    print(f"📞 call ended")
    print(f"📴 Call ended. Summary: {payload.get('summary')}")
    print("📜 Full transcript:", payload.get("transcript"))
    
    
def tool_call(event):
    print("in tool call")
    #executed when a tool is called
    with open('test.json', 'w') as f: json.dump(event, f, indent=2)
    event = request.json
    payload = event.get("message", {})
    event_type = payload.get("type")
    tool_name = payload.get("name")
    call_id = payload.get("call").get("id")
    tool_call_id= payload.get("toolCalls").get("id")
    args = payload.get("arguments", {})
    tool_response = {
                "results": [
            {
            "toolCallId": tool_name,
            "result": "Verified" }]
            }
    return tool_response

def function_call(event):
    #executed when a function is called
    print("in function call")
