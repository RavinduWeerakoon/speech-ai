import flask
import openai
import base64
from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv

import time
load_dotenv()
openai.api_key = os.getenv("API")


app = Flask(__name__)
#957ceae787fa45bd9e153891c61d0a8c

AUTHORIZATION = "957ceae787fa45bd9e153891c61d0a8c"
X_USER_ID = "pFbsSQAwCSN4S35gJgaeKO0eWYi1"



url_1 = "https://play.ht/api/v1/convert"
url_2 = "https://play.ht/api/v1/articleStatus?transcriptionId="
payload = {
    "content": ["Hello world"],
    "voice": "en-US-JennyNeural"
}
header_1 = {
    "accept": "application/json",
    "content-type": "application/json",
    "AUTHORIZATION": AUTHORIZATION,
    "X-USER-ID": X_USER_ID
}

header_2 = {
    "accept": "application/json",
    "AUTHORIZATION": AUTHORIZATION,
    "X-USER-ID": X_USER_ID
}

def convert(text):
    payload["content"] = [text]
    response = requests.post(url_1, json=payload, headers=header_1)

    t_id = response.json()["transcriptionId"]
    
    voice_url = url_2 + t_id
    time.sleep(3)
    url_response = requests.get(voice_url, headers=header_2)
    print(url_response.json())
    print(url_response)
    
    return url_response.json()["audioUrl"]

messages = [{'role':'system', 'content':"""
              Act as a QA bot the user will ask questions and answer them in the point form.
              Do not make the answers too long.Try to keep it below 100 words."""}]

def continue_conversation(messages, temperature=0.7):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=temperature, 
    )
    print(str(response.choices[0].message["content"]))
    return response.choices[0].message["content"]

def think(text):
    messages.append({'role':'user', 'content':f"{text}"})
    response = continue_conversation(messages)
    messages.append({'role':'assistant', 'content':f"{response}"})
    return response



@app.route('/')
def main():
    return render_template('index.html')

def create_audio():
    audio_file = open('audio.webm', "rb+")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    details = think(transcript)
    
   

    url = convert(details[:100])
    url = url.split("?")[0]
    
    return url
@app.route('/whisper', methods=['POST'])
def completion_api():
    
    data = request.files['audio_data'].read()
    with open('audio.webm', 'wb') as f:
        f.write(data)
    return create_audio()
    
@app.route('/completions', methods=['POST'])
def completion():
    json = request.json
    completion = openai.Completion.create(engine="text-davinci-003", prompt=request.prompt)
    return flask.Response(completion)

@app.route('/check', methods=['GET'])

def chck():
    

    audio_file = open('audio.webm', "rb+")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    details = think(transcript)

    return create_audio()

if __name__ == '__main__':
    app.run(debug=True)

