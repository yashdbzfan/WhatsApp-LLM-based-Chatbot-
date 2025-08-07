import os
from flask import Flask, request
from transformers import pipeline
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import json
from groq import Groq

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    from dotenv import load_dotenv
    load_dotenv(dotenv_path)

# Twilio and Groq credentials
acc_id = os.getenv("acc_id")
auth_token = os.getenv("auth_token")
api_key = os.getenv("api_key")
modele = os.getenv("modele")

app = Flask(__name__)   

# Ensure chat_history folder exists
CHAT_FOLDER = "chat_history"
os.makedirs(CHAT_FOLDER, exist_ok=True)
# Temporary in-memory user topic storage (consider Redis/DB for production)
user_topic_map = {}

def detect_topic(message, groq_client):
    instruction = (
        "You are a classifier. Classify the following message into ONLY one of these topics:\n"
        "- mental health\n"
        "- domestic violence\n"
        "- career guidance\n"
        "- emergency contact\n\n"
        "Reply with the exact topic name (e.g., 'emergency contact'). No explanation or additional text.\n"
        f"Message: \"{message}\""
    )

    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": instruction}],
            model=modele,
            temperature=0.7,
            stream=False,
        )

        if response and response.choices:
            detected_topic_raw = response.choices[0].message.content.strip().lower()
            print("💬 Groq response for topic detection:", detected_topic_raw)

            # Exact match against valid topics
            valid_topics = ["mental health", "domestic violence", "career guidance", "emergency contact"]
            if detected_topic_raw in valid_topics:
                print("✅ Detected topic:", detected_topic_raw)
                return detected_topic_raw

            # Fallback: Check for partial matches or synonyms
            for topic in valid_topics:
                if topic in detected_topic_raw or any(word in detected_topic_raw for word in topic.split()):
                    print("✅ Partial match detected for topic:", topic)
                    return topic

            # Handle specific cases for "emergency issues"
            if "emergency" in detected_topic_raw or "urgent" in detected_topic_raw:
                print("✅ Detected 'emergency' keyword, mapping to 'emergency contact'")
                return "emergency contact"

        print("❌ No valid topic matched. Returning 'unknown'.")
        return "unknown"

    except Exception as e:
        print("❌ Exception in detect_topic():", str(e))
        return "unknown"

def set_personality(topic="mental health"):
    personalities = {
        "mental health": {
            "role": "system",
            "content": "You are a compassionate and empathetic psychiatrist who helps people overcome depression and anxiety. "
            "Use simple, caring language."
        },
        "domestic violence": {
            "role": "system",
            "content": "You are a supportive counselor who helps victims of domestic violence. You provide clear, calm guidance "
            "and encourage them to seek help safely. Share helplines if necessary."
        },
        "career guidance": {
            "role": "system",
            "content": "You are a professional career coach who gives thoughtful advice on education, jobs, and personal development. "
            "Be inspiring and practical. Ask about their interests and goals."
        },
        "emergency contact": {
            "role": "system",
            "content": "You are an emergency assistant that helps users get urgent support. Be direct, ask for details, "
            "and guide them to nearest help or alert support staff if needed."
        }
    }
    return personalities.get(topic.lower(), personalities["mental health"])

def get_chat_file_path(user_id):
    return os.path.join(CHAT_FOLDER, f"{user_id}.json")

def chat_record(user_id, user_input, chatbot_response, sentiment):
    chat_file = get_chat_file_path(user_id)

    if os.path.exists(chat_file):
        with open(chat_file, "r") as file:
            chat_history = json.load(file)
    else:
        chat_history = []

    chat_history.append({
        "User Input": user_input,
        "Chatbot Response": chatbot_response,
        "Sentiment": sentiment
    })

    with open(chat_file, "w") as file:
        json.dump(chat_history, file)

def get_chat_history(user_id, max_messages=5):
    chat_file = get_chat_file_path(user_id)

    if os.path.exists(chat_file):
        with open(chat_file, "r") as file:
            chat_history = json.load(file)
        return chat_history[-max_messages:]
    
    return []

def sentiment_analyzer(text):
    sentiment_pipe = pipeline("sentiment-analysis",
                               model="cardiffnlp/twitter-roberta-base-sentiment-latest")
    truncated_text = text[:500]
    result = sentiment_pipe(truncated_text)
    return result[0]['label']

def summarize_text(text, max_length=400):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(text, max_length=max_length, min_length=100, do_sample=False)
    return summary[0]['summary_text']

def send_emergency_alert(sender_number, twilio_client):
    emergency_number = "whatsapp:+918690165889"
    message_body = f"The user {sender_number} is in a dire situation, please overlook"
    try:
        message = twilio_client.messages.create(
            to=emergency_number,
            from_='whatsapp:+14155238886',
            body=message_body
        )
        print("Emergency alert sent! SID:", message.sid)
    except Exception as e:
        print("❌ Failed to send emergency alert:", str(e))

@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "")
    sender_number = request.values.get("From", "")

    print(f"Received message from {sender_number}: {incoming_msg}")
    
    if incoming_msg.strip():
        respond_to_user(incoming_msg, sender_number)
    
    return str(MessagingResponse())

def respond_to_user(incoming_msg, sender_number):
    user_id = sender_number.replace("whatsapp:", "")
    groq_client = Groq(api_key=api_key)
    twilio_client = Client(acc_id, auth_token)

    # Handle "new session"
    if incoming_msg.lower().strip() == "new session":
        chat_file = get_chat_file_path(user_id)
        if os.path.exists(chat_file):
            os.remove(chat_file)
        user_topic_map[user_id] = None
        reply = (
            "Starting a new session. What do you need help with today?\n"
            "Please reply with one of the following:\n"
            "👉 mental health\n👉 domestic violence\n👉 career guidance\n👉 emergency contact"
        )

        twilio_client.messages.create(
            to=sender_number,
            from_='whatsapp:+14155238886',
            body=reply
        )
        print("New session started:", reply)
        return

    # Detect topic if not already set
    if user_id not in user_topic_map or user_topic_map[user_id] is None:
        topic = detect_topic(incoming_msg, groq_client)
        if topic in ["mental health", "domestic violence", "career guidance", "emergency contact"]:
            user_topic_map[user_id] = topic
            reply = f"Thanks! You selected *{topic}*. You can now tell me your concern."
            if topic == "emergency contact":
                send_emergency_alert(sender_number, twilio_client)
        else:
            reply = (
                "I'm not sure what you need help with.\n"
                "Please reply with one of the following:\n"
                "👉 mental health\n👉 domestic violence\n👉 career guidance\n👉 emergency contact"
            )

        twilio_client.messages.create(
            to=sender_number,
            from_='whatsapp:+14155238886',
            body=reply
        )
        print("Initial topic routing message sent:", reply)
        return

    # Topic is set, continue normal conversation
    topic = user_topic_map[user_id]
    if topic == "emergency contact":
        send_emergency_alert(sender_number, twilio_client)

    chat_history = get_chat_history(user_id)
    history_messages = []
    for chat in chat_history:
        history_messages.append({"role": "user", "content": chat["User Input"]})
        history_messages.append({"role": "assistant", "content": chat["Chatbot Response"]})

    personality_message = set_personality(topic)
    user_message = {"role": "user", "content": incoming_msg}

    chat_completion = groq_client.chat.completions.create(
        messages=[personality_message] + history_messages + [user_message],
        model=modele,
        stream=False,
    )

    chatbot_response = chat_completion.choices[0].message.content
    sentiment = sentiment_analyzer(incoming_msg)

    chat_record(user_id, incoming_msg, chatbot_response, sentiment)
    summary = summarize_text(chatbot_response, max_length=400)
    final_message = summary + f"\n(Sentiment: {sentiment})"

    message = twilio_client.messages.create(
        to=sender_number,
        from_='whatsapp:+14155238886',
        body=final_message
    )

    print("Message sent! SID:", message.sid)
    print("Topic used:", topic)
    print("Final message:", final_message)

if __name__ == "__main__":
    app.run(port=5000, debug=False)