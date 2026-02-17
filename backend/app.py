import os
import smtplib
import threading
import uuid
import time
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from flask import Flask, request, jsonify
from flask_cors import CORS
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
CORS(app)

@app.route('/')
def index():
    return app.send_static_file('index.html')

def send_email_thread(to_email, audio_filename, text_message):
    print(f"Background thread started for {to_email}", flush=True)
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")

    if not sender_email or not sender_password:
        print("Error: Email credentials not found.", flush=True)
        return

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = "You have a new voice message!"
    body = f"Here is the voice message for: \"{text_message}\""
    msg.attach(MIMEText(body, 'plain'))

    try:
        with open(audio_filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename=voice_message.mp3",
        )
        msg.attach(part)

        # Retry logic for connection
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Connecting to SMTP (Attempt {attempt+1})...", flush=True)
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30)
                server.login(sender_email, sender_password)
                server.send_message(msg)
                server.quit()
                print(f"Email sent successfully to {to_email}!", flush=True)
                break
            except Exception as e:
                print(f"SMTP Error (Attempt {attempt+1}): {e}", flush=True)
                time.sleep(2)
        
    except Exception as e:
        print(f"General Error in email thread: {e}", flush=True)
    finally:
        # Clean up file
        if os.path.exists(audio_filename):
            os.remove(audio_filename)
            print(f"Cleaned up {audio_filename}", flush=True)

@app.route('/api/send', methods=['POST'])
def send_voice_message():
    data = request.json
    email = data.get('email')
    message = data.get('message')

    if not email or not message:
        return jsonify({"error": "Email and message are required"}), 400

    try:
        # Generate Unique Filename
        unique_id = str(uuid.uuid4())
        audio_filename = f"message_{unique_id}.mp3"
        
        print(f"Generating TTS for {audio_filename}...", flush=True)
        tts = gTTS(text=message, lang='en')
        tts.save(audio_filename)
        
        # Start Background Thread
        print("Starting email background thread...", flush=True)
        thread = threading.Thread(target=send_email_thread, args=(email, audio_filename, message))
        thread.start()

        # Return Success Immediately
        return jsonify({"success": True, "message": "Sending in background..."}), 200

    except Exception as e:
        print(f"CRITICAL ERROR: {e}", flush=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
