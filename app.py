from flask import Flask, request, jsonify
from twilio.rest import Client
import requests
import openai
import base64
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TO_WHATSAPP = os.getenv("TO_WHATSAPP")
TWILIO_FROM = os.getenv("TWILIO_FROM")


openai.api_key = OPENAI_API_KEY
app = Flask(__name__)

# Upload to ImgBB
def upload_to_imgbb(image_path):
    with open(image_path, "rb") as file:
        res = requests.post(
            "https://api.imgbb.com/1/upload",
            params={"key": IMGBB_API_KEY},
            files={"image": file}
        )
    res.raise_for_status()
    return res.json()["data"]["url"]

@app.route('/analyze', methods=['POST'])
def analyze_image():
    file = request.files['file']
    filename = f"shrimp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    filepath = os.path.join("temp", filename)
    file.save(filepath)

    image_url = upload_to_imgbb(filepath)

    with open(filepath, "rb") as img_file:
        image_base64 = base64.b64encode(img_file.read()).decode("utf-8")

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": [
            {"type": "text", "text": "Analyze this shrimp for gut health, color, and visible diseases."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
        ]}
    ],
    max_tokens=500
)
analysis = response.choices[0].message.content


    # Send WhatsApp
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        from_=TWILIO_FROM,
        to=TO_WHATSAPP,
        body=f"📷 Shrimp Analysis:\n\n{analysis}",
        media_url=[image_url]
    )

    return jsonify({
        "image_url": image_url,
        "analysis": analysis,
        "whatsapp_status": message.status
    })

@app.route('/')
def home():
    return "Shrimp Analyzer Running ✅", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
