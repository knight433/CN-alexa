from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import speech_recognition as sr
import pyttsx3
import pygame
import threading
import os
from googlesearch import search
import socket
import time


global song_playing
song_playing = False

global alarmTime 

#model for the classification
model_name = "qanastek/XLMRoberta-Alexa-Intents-Classification"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
classifier = TextClassificationPipeline(model=model, tokenizer=tokenizer)

#to convert speech to text
def recognize_speech(pr="Say something:"):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        try:
            print(pr)
            recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
            audio = recognizer.listen(source, timeout=3)  # Listen to the microphone for up to 3 seconds
        except sr.exceptions.WaitTimeoutError:
            return ''

    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "UnknownValueError"
    except sr.RequestError as e:
        print("Could not request results from Google Web Speech API; {}".format(e))
    

#TTS (text to speach)
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    print(text)
    engine.runAndWait()

def change_volume(volume_level):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None
    ).QueryInterface(IAudioEndpointVolume)

    current_volume = round(interface.GetMasterVolumeLevelScalar(),1)

    #to increase volume 
    if volume_level == 1:
        volume = current_volume + 0.2
        
        #if vol max
        if current_volume == 1.0:
            toSpeak = "Volume is in the max level"
        
        volume = max(0.0, min(volume, 1.0))  
        toSpeak = "volume increased"     

    #to decrease volume
    elif volume_level == 2:
        volume = current_volume - 0.2

        if current_volume == 0:
            toSpeak = "Volume is in mute"

        volume = max(0.0, volume)
        toSpeak = "volume decreased"
    
    elif volume_level == 0:
        volume = 0
        toSpeak = "Volume muted"
    
    interface.SetMasterVolumeLevelScalar(volume, None)
    return toSpeak

#Genral greet, like hey or good morning
def general_greet():
    return 'hello, What can i do'

#to play music
def play(song):
    
    global current_song
    songs = ['shape of you','no cap']
    
    if song in songs:
        speak(f'playing {song}')
        music_file = os.path.join('C:/programs/projects/CN alexa/music', song + '.mp3')
        pygame.mixer.init()
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play()
        current_song = song

    elif 'stop' in song and current_song != None:
        pygame.mixer.music.stop()
        current_song = None

    elif 'pause' in song:
        pygame.mixer.music.pause()
    
    else:
        speak(f"Sorry, I don't have {song} in our playlist")

def play_music():

    global song_playing
    if song_playing == False:
        speak('sure, tell me which song do you want me to play:')
    
    while True:
        text = recognize_speech()
        
        if text == 'UnknownValueError':
            speak('can you repeat what your saying')
            text = recognize_speech()
        else:
            break
    
    music_thread = threading.Thread(target=play,args=(text,))
    music_thread.start()
    music_thread.join()  # Wait for the music thread to finish before returning
    song_playing = False


def lighton():
    raspberry_pi_address = 'raspberrypi'
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the Raspberry Pi server
    client_socket.connect((raspberry_pi_address, 5000))

    message = 'on'
    client_socket.sendall(message.encode('utf-8'))

    client_socket.close()

def lightoff():
    raspberry_pi_address = 'raspberrypi'
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the Raspberry Pi server
    client_socket.connect((raspberry_pi_address, 5000))

    message = 'off'
    client_socket.sendall(message.encode('utf-8'))

    client_socket.close()

def alarm():
    global alarmTime
    speak('Sure, tell me in what time')
    print('NOTE: please speak only the number of mins you need the alarm in ')
    inTime = recognize_speech(pr='Time')

    try:
        t = int(inTime)
        alarmTime = time.time() + t*60
        return f'Alarm set for {t} minutes from now.'
    except:
        speak('please speak only the number of mins you need the alarm in')
        return 'no alarm set'

#switch funtion
def execute(tag):
    t = ' '

    if tag == "audio_volume_up":
        t = change_volume(1)
    elif tag == "audio_volume_down":
        t = change_volume(2)
    elif tag == "audio_volume_mute":
        t = change_volume(0)
    elif tag == 'play_music':
        t = play_music()
    elif tag == 'general_greet': #need polish
        t = general_greet()
    elif tag == 'iot_light_on':
        t = lighton()
    elif tag == 'iot_light_off':
        t = lightoff()
    elif tag == 'alarm_set':
        t = alarm()
    else:
        pass
    
    speak(t)

def main():
    global alarmTime
    alarmTime = False
    while True:
        text = recognize_speech()
        
        if text == "UnknownValueError":
            speak("cant understand what your saying")
            text  = recognize_speech()
        elif text == 'stop':
            break
        
        if alarmTime:
            if alarmTime <= time.time():
                speak('TIME UP')
        
        try:
            res = classifier(text)
            tag = res[0]["label"]
            execute(tag)
            time.sleep(3)
        except:
            print('not able to classify due to noise')

        
    
if __name__ == "__main__":
    main()