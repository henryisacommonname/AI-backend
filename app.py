import os
from dotenv import load_dotenv
from flask import Flask,request, jsonify
from flask_cors import CORS
import json
from openai import OpenAI
# --- Config --- #
load_dotenv()
gpt_key = os.environ['chatGPT-API']
client = OpenAI(
    api_key = gpt_key 
)

app = Flask(__name__)
CORS(app)

def get_json_response(system_prompt, user_prompt):
    """
    Get a JSON response from the ChatGPT API.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    content = response.choices[0].message.content
    if content is None:
        raise ValueError("No content received from OpenAI API")
    return json.loads(content)

#  --- Routes --- #
@app.route('/health', methods=['GET'])
def health():
   return jsonify({"status": "running"})

@app.route('/chat_json', methods=['POST'])
def chat_json():
   try:
     data = request.get_json(force=True) or {}
     system_prompt = data.get('system_prompt')
     user_prompt = data.get('user_prompt')
     if not system_prompt or not user_prompt:
        return jsonify({"error": "Missing system_prompt or user_prompt"}), 400
     result = get_json_response(system_prompt, user_prompt)
     if not isinstance(result, dict):
         return jsonify({"error": "Model did not return a JSON object"}), 502
     return jsonify(result), 200
   except Exception as e:
     return jsonify({"error": "Upstream error", "detail": str(e)}), 500

if __name__ == '__main__':
  port = int(os.getenv("PORT", "8000"))  # default only used locally
  print("Starting on PORT:", os.getenv("PORT"))
  app.run(host='0.0.0.0', port=port)

