#!/usr/bin/env python3
# Requires PyAudio and PySpeech.

import speech_recognition as sr
from os import path


def input_filename (filename):
    # Read from wav
    AUDIO_FILE = path.join(path.join(path.dirname(path.realpath(__file__)), "uploads/" ), filename)


    r = sr.Recognizer()
    """
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)
    """
    # audio = wave.open(filename, "rb")
    print(AUDIO_FILE)
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)  # read the entire audio file

    # Speech recognition using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        #print("You said: " + r.recognize_google(audio, language='zh-TW'))
        return r.recognize_google(audio, language='zh-TW')
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
#    return r.recognize_google(audio, language='zh-TW')
"""
if __name__ == "__main__":
    input_filename("test.wav")
"""
