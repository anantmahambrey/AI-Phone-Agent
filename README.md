## Introduction
SalesBot.ai is a robust AI web agent capable of cold calling customers, holding meaningful conversations, and closing sales.

## Features
**Natural Language Understanding (NLU):** Understands and processes user intents effectively.
**Speech-to-Text (STT):** Converts user speech into text accurately using Google Gemini 1.5 Flash Model.
**Text-to-Speech (TTS):** Responds with natural-sounding voice output using the world's fastest smallest.ai Waves Lightning TTS model.
**Sales Assistance:** Tailored to assist in sales scenarios by guiding users through product information and closing deals.
**Conversational AI:** Supports a dynamic and interactive dialogue system.
**Customization:** Can be customized by the employee based on the customer, and reason for call.

## Technologies Used
**Frontend:** HTML, CSS, JavaScript (for user interface)    
**Backend:** Python, Django    
**Models and APIs:** Google Gemini 1.5 Flash Model (STT and conversational AI), Smallest.ai Waves Lightning Model (TTS)

## Installation
To run SalesBot.ai locally, follow these steps:

#### Clone the repository:
```git clone https://github.com/anantmahambrey/AI-Phone-Agent.git```
```cd AI-Phone-Agent```

#### Install the required packages: 
Make sure you have Python 3.12.0 installed. Create a virtual environment (optional) and install the dependencies:    
```pip install -r requirements.txt```

#### Run the application: 
Start the Django server:    
```python manage.py runserver```

#### Access the tool: 
Open your web browser and navigate to http://127.0.0.1:8000/

## Usage
Enter the company details and the details of the customer to whom the call is to be made.    
Click the Start Call button to Simulate the Call.    
Click on Start Speaking to speak to the bot ; Click on Stop Speaking to stop and wait for AI response.
Once AI responds, continue the conversation in the same way, or end call if you are done speaking.

## Model Details
-Google's Gemini 1.5 Flash is a fast and versatile multimodal model for scaling across diverse tasks.
We have used it for Text-to-Speech conversion and Speech-to-Speech conversations.
-Waves is smallest.ai's unified platform for speech synthesis. It supports various models designed for real-time applications such as voicebots.
Lightning is the world’s fastest text to speech model, generating around 10 seconds of hyper-realistic audio in just 100ms, all at once, no streaming.

