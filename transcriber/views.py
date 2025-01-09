# # transcriber/views.py
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
#             conversation_history = json.loads(request.POST.get('history', '[]'))
            
#             # Save the audio file temporarily
#             with tempfile.NamedTemporaryFile(delete=False, suffix='.m4a') as tmp_file:
#                 for chunk in audio_file.chunks():
#                     tmp_file.write(chunk)
#                 tmp_file_path = tmp_file.name

#             # Configure Gemini API
#             genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
            
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

#             # Start chat with history
#             chat_session = model.start_chat(history=conversation_history)
            
#             # First get transcription
#             transcription_response = chat_session.send_message(["Transcribe this audio. Only return the speech. Not any other noises.", myfile])
#             transcribed_text = transcription_response.text

#             # Then get AI response to transcribed text
#             ai_response = chat_session.send_message([
#                 "You are a salesperson, working for CapCount Technologies in Margao Goa."+
#                 "The user said: " + transcribed_text + 
#                 "Given the user's text and previous history," + 
#                 "\nPlease respond naturally and ask a follow-up question to continue the conversation."
#             ])

#             # Clean up temporary file
#             os.unlink(tmp_file_path)

#             return JsonResponse({
#                 'transcription': transcribed_text,
#                 'ai_response': ai_response.text,
#                 'history': conversation_history + [
#                     {"role": "user", "content": transcribed_text},
#                     {"role": "assistant", "content": ai_response.text}
#                 ]
#             })
            
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
    
#     return JsonResponse({'error': 'Invalid request'}, status=400)

# transcriber/views.py
import os
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
import tempfile

def index(request):
    return render(request, 'transcriber/index.html')

@csrf_exempt
def transcribe(request):
    if request.method == 'POST':
        try:
            audio_file = request.FILES['audio']
            # We'll still receive the history but won't pass it to Gemini directly
            conversation_history = json.loads(request.POST.get('history', '[]'))
            
            # Save the audio file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.m4a') as tmp_file:
                for chunk in audio_file.chunks():
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name

            # Configure Gemini API
            genai.configure(api_key="AIzaSyDxiigaZNe4TTzdDojZOoQfOC-PjnTLiw4")
            
            # Upload file to Gemini
            myfile = genai.upload_file(tmp_file_path)

            # Create the model
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

            # Start a new chat session each time
            chat = model.start_chat()
            
            # If there's conversation history, provide context
            if conversation_history:
                context = "Previous conversation:\n"
                for msg in conversation_history:
                    role = "User" if msg["role"] == "user" else "Assistant"
                    context += f"{role}: {msg['content']}\n"
                chat.send_message(context)

            # Get transcription
            transcription_response = chat.send_message(["Transcribe this audio. Only return the speech. Not any other noises.", myfile])
            transcribed_text = transcription_response.text

            # Get AI response to transcribed text
            prompt = f"You are a salesperson, working for CapCount Technologies in Margao Goa. The user said: {transcribed_text}\n Given the user's prompt and the previous chat history, Please respond naturally and ask a follow-up question to continue the conversation."
            ai_response = chat.send_message(prompt)

            # Clean up temporary file
            os.unlink(tmp_file_path)

            # Update conversation history
            conversation_history.append({"role": "user", "content": transcribed_text})
            conversation_history.append({"role": "assistant", "content": ai_response.text})

            return JsonResponse({
                'transcription': transcribed_text,
                'ai_response': ai_response.text,
                'history': conversation_history
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)