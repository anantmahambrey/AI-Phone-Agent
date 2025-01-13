# transcriber/views.py
import os
import json
import base64
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import google.generativeai as genai
import tempfile
import requests

url = "https://waves-api.smallest.ai/api/v1/lightning/get_speech"

def form(request):
    return render(request, 'transcriber/form.html')

def start_call(request):
    if request.method == 'POST':
        # Store form data in session
        request.session['call_details'] = {
            'company_name': request.POST.get('company_name'),
            'company_type': request.POST.get('company_type'),
            'company_domain': request.POST.get('company_domain'),
            'ai_name': request.POST.get('ai_name'),
            'user_name': request.POST.get('user_name'),
            'customer_type': request.POST.get('customer_type'),
            'reason': request.POST.get('reason'),
            'mail_id': request.POST.get('mail_id'),
            'company_details': request.POST.get('company_details'),
        }
        return redirect('index')
    return redirect('form')

def index(request):
    # Check if call details exist in session
    if 'call_details' not in request.session:
        return redirect('form')
    return render(request, 'transcriber/index.html', {
        'call_details': request.session['call_details']
    })

def endCall(request):
    return redirect('form')

@csrf_exempt
def transcribe(request):
    if request.method == 'POST':
        try:
            audio_file = request.FILES['audio']
            conversation_history = json.loads(request.POST.get('history', '[]'))
            
            # Get call details from session
            call_details = request.session.get('call_details', {})
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.m4a') as tmp_file:
                for chunk in audio_file.chunks():
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name

            genai.configure(api_key="AIzaSyDxiigaZNe4TTzdDojZOoQfOC-PjnTLiw4")
            myfile = genai.upload_file(tmp_file_path)

            generation_config = {
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            }

            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
            )

            chat = model.start_chat()

            initial_context = f"""Role: Professional AI Sales Agent
                Name: {call_details.get('ai_name')} ,
                Company Name: {call_details.get('company_name')} ,
                Company Type : {call_details.get('company_type')} ,
                Domain: {call_details.get('company_domain')} ,
                Company Contact: {call_details.get('mail_id')} ,
                Company Details: {call_details.get('company_details')}

                Target Customer:
                Name: {call_details.get('user_name')}
                Type: {call_details.get('customer_type')}

                Call Purpose:
                {call_details.get('reason')}

                Core Guidelines:
                Response Length: Keep responses under 50 words.
                Follow-Up Questions: Ask one relevant follow-up question per response to maintain engagement.
                Confirmation: Always wait for customer confirmation before proceeding to the next step.
                Sequential Flow: Follow the conversation protocol strictly without skipping steps.

                Conversation Protocol:

                Opening (Mandatory Script):
                Script: "Hello, this is {call_details.get('ai_name')} calling from {call_details.get('company_name')}. Am I speaking with {call_details.get('user_name')}?"
                If No: Verify once, apologize, and end the call.
                If Yes: Proceed to the availability check.

                Availability Check:
                Ask: "Is this a convenient time to talk?"
                If Interrupting: Apologize and offer to reschedule.
                If Convenient: Proceed with the conversation.

                Company Introduction:
                Provide a brief overview of the company.
                Highlight the value proposition and how it aligns with the customer's needs.
                Build rapport by showing genuine interest in the customer.

                Call Purpose:
                Clearly articulate the reason for the call.
                Align the conversation with the customer's context and previous interactions (if any).
                Avoid repetition unless the customer requests it.

                Engagement Guidelines:
                Active Listening: Pay close attention to the customer's responses and adjust accordingly.
                Personalization: Tailor responses based on customer feedback and cues.

                Transparency:
                If asked for information not provided in the call details, respond with:
                "I'll have someone follow up with those details via {call_details.get('mail_id')}."
                Never provide unverified or speculative information.

                Response Scenarios:
                a) If Customer Shows Interest:
                Guide them through the next steps as per the call objective.
                Be specific about action items and timelines.

                b) If Customer Is Hesitant:
                Offer to provide follow-up information.
                Propose a specific callback time.
                Share the email contact: {call_details.get('mail_id')}.

                c) If Customer Raises Concerns:
                Address concerns professionally and empathetically.
                Focus on understanding their perspective.
                Provide factual responses only.

                Call Conclusion:
                Summarize key points discussed.
                Confirm next steps (if any).
                Express gratitude for their time, regardless of the outcome.
                Provide contact information if needed.

                Language Protocol:
                Communicate strictly in English unless the customer specifies otherwise.

                Previous Conversation Context:"""
            
            if conversation_history:
                for msg in conversation_history:
                    role = "Customer" if msg["role"] == "user" else "AI Assistant"
                    initial_context += f"\n{role}: {msg['content']}"
            
            chat.send_message(initial_context)

            transcription_response = chat.send_message(["This is what the customer said. Transcribe this audio. Only return the speech. Not any other noises.", myfile])
            transcribed_text = transcription_response.text

            prompt = f"The customer said: {transcribed_text}. Please respond naturally according to the instructions mentioned earlier. Check the conversation history, and do not repeat responses. Just give the response. Do not include 'AI Assistant:'"
            ai_response = chat.send_message(prompt)



            tts_url = "https://waves-api.smallest.ai/api/v1/lightning/get_speech"
            tts_payload = {
                "voice_id": "ananya",
                "text": ai_response.text,
                "speed": 1.15,
                "sample_rate": 24000,
                "add_wav_header": True
            }
            tts_headers = {
                "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NzgyOTAzMjQzNjMwNGZhZDUwNmZjNWUiLCJ0eXBlIjoiYXBpS2V5IiwiaWF0IjoxNzM2NjA5ODQyLCJleHAiOjQ4OTIzNjk4NDJ9.JIgBP60WI5Ni85ted6CYX4DCImn97lpjX-JQjNu-pLA",
                "Content-Type": "application/json"
            }
            
            tts_response = requests.post(tts_url, json=tts_payload, headers=tts_headers)
            
            if tts_response.status_code == 200:
                # Convert audio data to base64 for sending to frontend
                audio_base64 = base64.b64encode(tts_response.content).decode('utf-8')
            else:
                audio_base64 = None



            os.unlink(tmp_file_path)

            conversation_history.append({"role": "user", "content": transcribed_text})
            conversation_history.append({"role": "assistant", "content": ai_response.text})

            return JsonResponse({
                'transcription': transcribed_text,
                'ai_response': ai_response.text,
                'audio_data': audio_base64,
                'history': conversation_history
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
    