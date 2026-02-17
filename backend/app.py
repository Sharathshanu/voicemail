import os
import smtplib
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

def send_email_with_audio(to_email, audio_filename, text_message):
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")

    if not sender_email or not sender_password:
        print("Error: Email credentials not found in environment variables.")
        return False

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
            f"attachment; filename= {os.path.basename(audio_filename)}",
        )
        msg.attach(part)

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/api/send', methods=['POST'])
def send_voice_message():
    data = request.json
    email = data.get('email')
    message = data.get('message')

    if not email or not message:
        return jsonify({"error": "Email and message are required"}), 400

    try:
        print("Starting request processing...", flush=True)
        # Generate Audio
        print("Generating TTS...", flush=True)
        tts = gTTS(text=message, lang='en')
        audio_filename = "message.mp3"
        tts.save(audio_filename)
        print("TTS Generated.", flush=True)

        # Send Email
        print(f"Attempting to send email to {email}...", flush=True)
        if send_email_with_audio(email, audio_filename, message):
            print("Email sent successfully!", flush=True)
            # Clean up
            if os.path.exists(audio_filename):
                os.remove(audio_filename)
            return jsonify({"success": True, "message": "Voice message sent successfully!"}), 200
        else:
             print("Email sending failed.", flush=True)
             return jsonify({"error": "Failed to send email. Check server logs."}), 500

    except Exception as e:
        print(f"CRITICAL ERROR: {e}", flush=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
