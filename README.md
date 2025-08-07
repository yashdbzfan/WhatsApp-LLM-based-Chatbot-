# **WhatsApp Intelligent Chatbot with Multi-Domain Support**

## **Overview**

This project implements an intelligent **WhatsApp chatbot** that provides specialized support across **4 distinct domains**: mental health, domestic violence, career guidance, and emergency contact. The system leverages **Groq LLM** for automatic topic classification, **transformers** for sentiment analysis and text summarization, and integrates seamlessly with **Twilio WhatsApp Business API**. The chatbot features persistent chat history, emergency alert functionality, and real-time webhook processing via **ngrok tunneling**. All conversations are analyzed for emotional context and summarized for optimal message delivery.

## **Features**

### **Core Functionality**

- **Multi-Domain Support**: Specialized AI personalities for mental health counseling, domestic violence support, career guidance, and emergency assistance
- **Automatic Topic Classification**: **Groq LLM**-powered topic detection from user messages with fallback mechanisms
- **Real-time Webhook Integration**: Seamless **WhatsApp Business API** connectivity via **Twilio** and **ngrok** tunneling
- **Emergency Response System**: Automatic alert notifications to support staff for crisis situations


### **AI \& NLP Features**

- **Sentiment Analysis**: **Cardiff RoBERTa** model for emotional context understanding with **500-character optimization**
- **Text Summarization**: **Facebook BART-Large-CNN** model compressing responses to **400-character limits**
- **Conversation Context**: Maintains chat history with configurable message retention (**5 recent messages**)
- **Session Management**: User-specific topic mapping with session reset functionality


### **Technical Features**

- **Persistent Storage**: **JSON-formatted** chat history with sentiment tracking
- **Environment Security**: Credential management via **.env** configuration
- **Cross-Platform Support**: Compatible with **Windows**, **macOS**, and **Linux**
- **Scalable Architecture**: **Flask**-based backend with modular design


## **Project Structure**

```
whatsapp-chatbot/
├── app.py                 # Main Flask application with webhook handling
├── .env                   # Environment variables (Twilio, Groq credentials)
├── .env.example          # Template for environment configuration
├── ngrok.rar             # ngrok executable (requires extraction)
├── chat_history/         # Directory for storing user conversations
│   └── [user_conversations].json
├── requirements.txt      # Python dependencies
├── README.md            # This documentation file
└── .gitignore           # Git ignore patterns
```


## **Requirements**

### **Python Dependencies**

```
flask==2.3.3
transformers==4.35.2
torch==2.1.0
twilio==8.10.0
groq==0.4.1
python-dotenv==1.0.0
```


### **External Services**

- **Twilio Account**: WhatsApp Business API access
- **Groq API**: LLM service for topic classification
- **ngrok**: Local tunnel for webhook endpoints


### **System Requirements**

- **Python 3.8+**
- **4GB RAM** (minimum for transformer models)
- **Internet connection** for API services


## **Setup Instructions**

### **1. Clone the Repository**

```bash
git clone <repository-url>
cd whatsapp-chatbot
```


### **2. Extract ngrok**

```bash
# Extract ngrok.rar file
# Windows: Use WinRAR or 7-Zip
# macOS/Linux: Use unrar or archive manager
unrar x ngrok.rar
# Make ngrok executable (macOS/Linux)
chmod +x ngrok
```


### **3. Install Python Dependencies**

```bash
pip install -r requirements.txt
```


### **4. Environment Configuration**

Create a `.env` file in the project root:

```env
acc_id=your_twilio_account_sid
auth_token=your_twilio_auth_token
api_key=your_groq_api_key
modele=llama3-70b-8192
```

**Required Credentials:**

- **Twilio Account SID**: From Twilio Console Dashboard
- **Twilio Auth Token**: From Twilio Console Dashboard
- **Groq API Key**: From Groq Console (https://console.groq.com)
- **Model Name**: Groq model identifier (e.g., `llama3-70b-8192`)


### **5. Twilio WhatsApp Setup**

1. **Enable WhatsApp Sandbox**: In Twilio Console → Messaging → Try it out → Send a WhatsApp message
2. **Join Sandbox**: Send specified message to **+1 415 523 8886**
3. **Configure Webhook**: Set webhook URL (will be provided by ngrok in step 7)

### **6. Start the Flask Application**

```bash
python app.py
```

Application starts on **http://localhost:5000**

### **7. Setup ngrok Tunnel**

Open a **new terminal** and run:

```bash
# Windows
.\ngrok.exe http 5000

# macOS/Linux  
./ngrok http 5000
```

**Copy the HTTPS URL** (e.g., `https://abcd1234.ngrok.io`) and configure it in **Twilio Console**:

- **Webhook URL**: `https://your-ngrok-url.ngrok.io/webhook`
- **HTTP Method**: `POST`


### **8. Test the Connection**

Send a message to your **Twilio WhatsApp number** to verify the setup.

## **Usage**

### **Starting a Conversation**

1. **Send any message** to the Twilio WhatsApp number
2. **System will auto-detect topic** or prompt for selection:
    - 👉 **mental health**
    - 👉 **domestic violence**
    - 👉 **career guidance**
    - 👉 **emergency contact**

### **Session Management**

- **New Session**: Send `"new session"` to reset conversation history
- **Topic Switch**: Send a new topic keyword to change domains
- **Emergency**: System automatically alerts support staff for crisis situations


### **Conversation Flow**

1. **Topic Detection**: AI classifies user intent
2. **Personality Loading**: System adapts to domain-specific responses
3. **Context Processing**: Maintains conversation history (5 messages)
4. **Response Generation**: Groq LLM generates contextual responses
5. **Sentiment Analysis**: Cardiff RoBERTa analyzes emotional state
6. **Summarization**: BART model optimizes response length
7. **Delivery**: Final message sent via WhatsApp with sentiment indicator

## **System Architecture**

### **AI Pipeline**

```
User Message → Topic Classification → Personality Selection → Context Loading → 
LLM Processing → Sentiment Analysis → Text Summarization → WhatsApp Delivery
```


### **Domain Personalities**

- **Mental Health**: Compassionate psychiatrist approach, depression/anxiety focus
- **Domestic Violence**: Supportive counselor, safety-focused guidance
- **Career Guidance**: Professional coach, education and development oriented
- **Emergency Contact**: Direct assistant, crisis intervention protocols


### **Emergency System**

When **emergency contact** is detected:

1. **Immediate Alert**: Notification sent to support staff (`+918690165889`)
2. **Crisis Protocol**: Direct, urgent response personality activated
3. **Priority Processing**: Emergency messages bypass normal queuing

## **API Integration Details**

### **Groq LLM Integration**

```python
# Topic Classification
groq_client.chat.completions.create(
    messages=[{"role": "user", "content": classification_prompt}],
    model="llama3-70b-8192",
    temperature=0.7
)
```


### **Twilio WhatsApp API**

```python
# Message Sending
client.messages.create(
    to="whatsapp:+1234567890",
    from_="whatsapp:+14155238886", 
    body=message_content
)
```


### **Transformer Models**

- **Sentiment**: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- **Summarization**: `facebook/bart-large-cnn`


## **Example Conversation**

### **Initial Contact**

```
User: "I'm feeling really anxious lately"
System: "Thanks! You selected *mental health*. You can now tell me your concern."
```


### **Conversation Flow**

```
User: "I can't sleep and keep having panic attacks"
Bot: "I understand how frightening panic attacks can be. Let's work through some 
      grounding techniques that can help... [summarized response]
      (Sentiment: NEGATIVE)"
```


### **Emergency Scenario**

```
User: "I need help urgently"  
System: [Automatically alerts support staff]
Bot: "I'm here to help you right away. Can you tell me more about your situation? 
     I've also alerted our support team. (Sentiment: NEGATIVE)"
```


## **Chat History Format**

```json
[
  {
    "User Input": "I'm having trouble sleeping",
    "Chatbot Response": "Sleep difficulties can be challenging...",
    "Sentiment": "NEGATIVE"
  }
]
```


## **Troubleshooting**

### **Common Issues**

#### **ngrok Connection Failed**

```bash
# Check if ngrok is running
./ngrok http 5000

# Verify webhook URL in Twilio Console
# Ensure HTTPS URL is used (not HTTP)
```


#### **Twilio Authentication Error**

```bash
# Verify credentials in .env file
# Check Twilio Account SID and Auth Token
# Ensure WhatsApp sandbox is properly configured
```


#### **Model Loading Issues**

```bash
# Clear transformer cache
rm -rf ~/.cache/huggingface/

# Reinstall transformers
pip uninstall transformers torch
pip install transformers torch
```


#### **Environment Variables Not Loading**

```bash
# Verify .env file exists and format:
acc_id=ACxxxxxxx
auth_token=xxxxxxx
api_key=gsk_xxxxxxx
modele=llama3-70b-8192

# Check file permissions
ls -la .env
```


#### **Port Conflicts**

```bash
# Change Flask port in app.py
app.run(port=5001, debug=False)

# Update ngrok accordingly  
./ngrok http 5001
```


#### **Webhook Not Receiving Messages**

1. **Verify ngrok tunnel** is active and HTTPS URL is correct
2. **Check Twilio webhook configuration** matches ngrok URL
3. **Ensure WhatsApp sandbox** is joined and active
4. **Test webhook endpoint** directly: `curl https://your-ngrok-url.ngrok.io/webhook`

#### **Emergency Alerts Not Sending**

```bash
# Verify emergency contact number format
emergency_number = "whatsapp:+918690165889"

# Check Twilio account has international messaging enabled
# Ensure recipient has joined WhatsApp sandbox
```


### **Debug Mode**

Enable detailed logging by modifying **app.py**:

```python
app.run(port=5000, debug=True)
```


### **Performance Optimization**

- **Reduce model size**: Use smaller transformer variants for limited resources
- **Implement caching**: Store frequent responses to reduce API calls
- **Batch processing**: Queue multiple messages for efficient processing


## **Contributing**

1. **Fork the repository**
2. **Create feature branch** (`git checkout -b feature/enhancement`)
3. **Commit changes** (`git commit -am 'Add new feature'`)
4. **Push to branch** (`git push origin feature/enhancement`)
5. **Create Pull Request**

**⚠️ Important Security Notes:**

- Never commit `.env` file to version control
- Regularly rotate API keys and tokens
- Use HTTPS endpoints for all webhook configurations
- Monitor emergency alert functionality regularly

