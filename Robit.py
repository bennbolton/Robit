from RobitUI import RobitUI
import speech_recognition as sr

class Robit():
    def __init__(self):
        self.ui = RobitUI()

    def listen(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print('Listening....')
            r.pause_threshold = 1
            audio = r.listen(source)    
        try:
            print('Recognizing...')
            query = r.recognize_google(audio, language='en-gb')
            print(query)
        except Exception:
            self.say('Sorry, I could not understand. Could you please say that again?')
            query = None
        return query

    def say(self, string:str):
        raise NotImplementedError


    def update(self):
        self.ui.update()