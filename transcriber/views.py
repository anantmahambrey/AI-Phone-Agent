# import os
# import json
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import google.generativeai as genai
# import tempfile

# def index(request):
#     return render(request, 'transcriber/index.html')

# @csrf_exempt
# def transcribe(request):
#     if request.method == 'POST':
#         try:
#             audio_file = request.FILES['audio']
#             # We'll still receive the history but won't pass it to Gemini directly
#             conversation_history = json.loads(request.POST.get('history', '[]'))
            
#             # Save the audio file temporarily
#             with tempfile.NamedTemporaryFile(delete=False, suffix='.m4a') as tmp_file:
#                 for chunk in audio_file.chunks():
#                     tmp_file.write(chunk)
#                 tmp_file_path = tmp_file.name

#             # Configure Gemini API
#             genai.configure(api_key="AIzaSyDxiigaZNe4TTzdDojZOoQfOC-PjnTLiw4")
            
#             # Upload file to Gemini
#             myfile = genai.upload_file(tmp_file_path)

#             # Create the model
#             generation_config = {
#                 "temperature": 1,
#                 "top_p": 0.95,
#                 "top_k": 40,
#                 "max_output_tokens": 8192,
#                 "response_mime_type": "text/plain",
#             }

#             model = genai.GenerativeModel(
#                 model_name="gemini-1.5-flash",
#                 generation_config=generation_config,
#             )

#             # Start a new chat session each time
#             chat = model.start_chat()
            
#             # If there's conversation history, provide context
#             if conversation_history:
#                 context = "Previous conversation:\n"
#                 for msg in conversation_history:
#                     role = "User" if msg["role"] == "user" else "Assistant"
#                     context += f"{role}: {msg['content']}\n"
#                 chat.send_message(context)

#             # Get transcription
#             transcription_response = chat.send_message(["Transcribe this audio. Only return the speech. Not any other noises.", myfile])
#             transcribed_text = transcription_response.text

#             # Get AI response to transcribed text
#             prompt = f"You are a salesperson, working for CapCount Technologies in Margao Goa. The user said: {transcribed_text}\n Given the user's prompt and the previous chat history, Please respond naturally and ask a follow-up question to continue the conversation."
#             ai_response = chat.send_message(prompt)

#             # Clean up temporary file
#             os.unlink(tmp_file_path)

#             # Update conversation history
#             conversation_history.append({"role": "user", "content": transcribed_text})
#             conversation_history.append({"role": "assistant", "content": ai_response.text})

#             return JsonResponse({
#                 'transcription': transcribed_text,
#                 'ai_response': ai_response.text,
#                 'history': conversation_history
#             })
            
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
    
#     return JsonResponse({'error': 'Invalid request'}, status=400)

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
                Name: {call_details.get('ai_name')}
                Company: {call_details.get('company_name')} ({call_details.get('company_type')})
                Domain: {call_details.get('company_domain')}
                Contact: {call_details.get('mail_id')}

                Target Customer:
                - Name: {call_details.get('user_name')}
                - Type: {call_details.get('customer_type')}

                Call Purpose:
                {call_details.get('reason')}
                Please follow the core guidelines while carrying out the call.
                
                Core Guidelines:

                Keep responses under 70 words.
                Try to ask one follow-up question per response.
                Wait for confirmation before proceeding.
                Carry out the call sequantially ONLY according to the conversation protocol mentioned below.


                Conversation Protocol:
                1. Opening (Mandatory Script):
                "Hello, this is {call_details.get('ai_name')} calling from {call_details.get('company_name')}. Am I speaking with {call_details.get('user_name')}?"
                - If no → Verify once, apologize, and end call
                - If yes → Proceed to availability check

                2. Availability Check:
                - Ask if this is a convenient time to talk
                - If interrupting → Apologize and offer to reschedule
                - If convenient → Proceed with conversation

                3. Company Introduction:
                - Provide brief company overview
                - Focus on value proposition
                - Build rapport before discussing business

                4. Call Purpose:
                - Clearly articulate reason for call
                - Align with previous conversation context
                - Avoid repetition unless requested

                5. Engagement Guidelines:
                - Practice active listening
                - Personalize responses based on customer feedback
                - Handle questions with transparency:
                    → If any specific information about the company or product asked to you is not told to you in the reason for call and instructions above, 
                    reply with "I'll have someone follow up with those details via {call_details.get('mail_id')}". 
                    → Never provide unverified information not told to you.

                6. Response Scenarios:
                a) If Customer Shows Interest:
                    - Guide through next steps as per call objective
                    - Be specific about action items
                
                b) If Customer Is Hesitant:
                    - Offer follow-up information
                    - Propose specific callback time
                    - Share email contact: {call_details.get('mail_id')}

                c) If Customer Raises Concerns:
                    - Address professionally
                    - Focus on understanding
                    - Provide factual responses only

                7. Call Conclusion:
                - Summarize key points
                - Confirm next steps (if any)
                - Express gratitude regardless of outcome
                - Provide contact information if needed

                Language Protocol: Communication strictly in English unless otherwise specified.

                Previous Conversation Context:"""
            
            if conversation_history:
                for msg in conversation_history:
                    role = "Customer" if msg["role"] == "user" else "AI Assistant"
                    initial_context += f"\n{role}: {msg['content']}"
            
            chat.send_message(initial_context)

            transcription_response = chat.send_message(["This is what the customer said. Transcribe this audio. Only return the speech. Not any other noises.", myfile])
            transcribed_text = transcription_response.text

            prompt = f"The customer said: {transcribed_text}. Please respond naturally according to the instructions mentioned earlier."
            ai_response = chat.send_message(prompt)



            tts_url = "https://waves-api.smallest.ai/api/v1/lightning/get_speech"
            tts_payload = {
                "voice_id": "deepika",
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
    