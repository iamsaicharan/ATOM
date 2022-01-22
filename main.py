import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser
import os
from datetime import date
import psutil
import time
from sys import byteorder
from array import array
from struct import pack
import pyaudio
import wave

firefoxPath = 'C:\\Program Files\\Mozilla Firefox\\firefox.exe'
webbrowser.register('firefox', None, webbrowser.BackgroundBrowser(firefoxPath))
THRESHOLD = 500
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 44100

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
# print(voices[0].id)
engine.setProperty('voice', voices[0].id)
rate = engine.getProperty('rate')
print(rate)
engine.setProperty('rate', 175)


def is_silent(snd_data):
    "Returns 'True' if below the 'silent' threshold"
    return max(snd_data) < THRESHOLD

def normalize(snd_data):
    "Average the volume out"
    MAXIMUM = 16384
    times = float(MAXIMUM)/max(abs(i) for i in snd_data)

    r = array('h')
    for i in snd_data:
        r.append(int(i*times))
    return r

def trim(snd_data):
    "Trim the blank spots at the start and end"
    def _trim(snd_data):
        snd_started = False
        r = array('h')

        for i in snd_data:
            if not snd_started and abs(i)>THRESHOLD:
                snd_started = True
                r.append(i)

            elif snd_started:
                r.append(i)
        return r

    # Trim to the left
    snd_data = _trim(snd_data)

    # Trim to the right
    snd_data.reverse()
    snd_data = _trim(snd_data)
    snd_data.reverse()
    return snd_data

def add_silence(snd_data, seconds):
    "Add silence to the start and end of 'snd_data' of length 'seconds' (float)"
    silence = [0] * int(seconds * RATE)
    r = array('h', silence)
    r.extend(snd_data)
    r.extend(silence)
    return r

def record():

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=1, rate=RATE,
        input=True, output=True,
        frames_per_buffer=CHUNK_SIZE)

    num_silent = 0
    snd_started = False

    r = array('h')

    while 1:
        # little endian, signed short
        snd_data = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            snd_data.byteswap()
        r.extend(snd_data)

        silent = is_silent(snd_data)

        if silent and snd_started:
            num_silent += 1
        elif not silent and not snd_started:
            snd_started = True

        if snd_started and num_silent > 30:
            break

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    r = normalize(r)
    r = trim(r)
    r = add_silence(r, 0.5)
    return sample_width, r

def record_to_file(path):
    "Records from the microphone and outputs the resulting data to 'path'"
    sample_width, data = record()
    data = pack('<' + ('h'*len(data)), *data)

    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()

print('Please enter the passcode')
passcode = input()

newname = print(datetime.datetime.now())
print(type(newname))

if '08051998' == passcode:
    def speak(audio):
        engine.say(audio)
        engine.runAndWait()

    #speak('Welcome back sir')

    def wiseMe():
        hour = int(datetime.datetime.now().hour)
        if hour >= 0 and hour < 12:
            speak('Good morning sir  ')
            speak('Atom up and running')
            startime = datetime.datetime.now().strftime('%H:%M')
            speak(f"it's {startime}")
            

        elif hour >= 12 and hour < 18:
            speak('Good afternoon sir  ')
            speak("Atom up and running")
            startime = datetime.datetime.now().strftime('%H:%M')
            speak(f"it's {startime}")


        else:
            speak('Good evening sir  ')
            speak("Atom up and running")
            startime = datetime.datetime.now().strftime('%H:%M')
            speak(f"it's {startime}")        

        battery = psutil.sensors_battery()
        plugged = battery.power_plugged
        percent = str(battery.percent)
        if plugged==False: plugged="Not Plugged In"
        else: plugged="Plugged In"
        speak("Battery is running at " + percent + "%" + "and the charging port is" + plugged)
        speak('system performance is at its normal stage')


    def takeCommand():

        r = sr.Recognizer()
        with sr.Microphone() as source:
            print('Listening...')
            r.pause_threshold = 0.5
            audio = r.listen(source)

        try:
            print('Recognizing...')
            query = r.recognize_google(audio, language='en-in')
            print(f"User said: {query}\n")

        except Exception as e:
            print(e)
            print('can you please repeat it boss')
            return 'None'

        return query


    if __name__ == '__main__':
        wiseMe()
        while True:
            # query = takeCommand().lower()
            query = input()

            if 'wikipedia' in query:
                speak('Searching wikipedia..')
                query = query.replace('wikipedia', '')
                results = wikipedia.summary(query, sentences=2)
                speak('According to wikipedia')
                print(results)
                speak(results)

            elif 'google' in query:
                speak('Searching google..')
                query = query.replace('google ', '')
                path = "https://www.google.com/search?client=firefox-b-d&q=" + query
                webbrowser.get('firefox').open_new_tab(path)

            elif 'hello atom' in query:
                speak("hello sir")

            elif 'this is atom' in query:
                file1 = open("C:\\Users\\S.R.I.O.U.S\\Desktop\\A.T.O.M\\logs\\info.txt", "r")
                text1 = file1.readlines()
                speak(text1)

            elif 'atom' in query and 'open youtube' in query:
                speak("in a second")
                webbrowser.get('firefox').open_new_tab('youtube.com')

            elif 'atom' in query and 'news' in query:
                webbrowser.get('firefox').open_new_tab('https://www.youtube.com/watch?v=zR7HkEa3Swg')

            elif 'atom' in query and 'work music' in query:
                music_dir = 'C:\\Users\\S.R.I.O.U.S\\Music\\iTunes\\iTunes Media\\Music'
                songs = os.listdir(music_dir)
                print(songs)
                os.startfile(os.path.join(music_dir, songs[0]))

            elif 'atom' in query and 'time' in query:
                startime = datetime.datetime.now().strftime('%H:%M')
                speak(f"it's {startime} sir")

            elif 'atom' in query and 'about your boss' in query:
                file1 = open("C:\\Users\\S.R.I.O.U.S\\Desktop\\A.T.O.M\\logs\\about me.txt", "r")
                text1 = file1.readlines()
                speak(text1)
                

            elif 'atom' in query and 'new project' in query:
                speak('What should i name it sir?')
                query = takeCommand().upper()
                os.chdir('E:\\S.R.I.O.U.S\\PROJECTS')
                os.mkdir(query)
                speak('Creating new file\n')
                speak('Opening the folder')
                os.startfile('E:\\S.R.I.O.U.S\\PROJECTS')

            elif 'atom' in query and 'record' in query:
                timestamp = datetime.datetime.now()
                timestampstr = str(timestamp)
                timestampstr = timestampstr.split(":")[0]
                filename = "recording " + timestampstr + ".wav"
                path = "C:\\Users\\S.R.I.O.U.S\\Desktop\\A.T.O.M\\records\\" + filename
                speak("Recording it now...")
                record_to_file(path)
                speak("saving the file now...")
                

            elif 'atom' in query and 'log' in query:
                timestamp = datetime.datetime.now()
                timestampstr = str(timestamp)
                timestampstr = timestampstr.split(":")[0]
                filename = "log " + timestampstr + ".txt"
                path = "C:\\Users\\S.R.I.O.U.S\\Desktop\\A.T.O.M\\logs\\" + filename
                file = open(path, "w+")
                speak('Sure, do you want to dictate or type it sir')
                logchoice = takeCommand().lower()
                if 'dictate' in logchoice:
                    info = takeCommand().lower()
                    file.write(info)
                    file.close()

                elif 'type' in logchoice or 'write' in logchoice:
                    info = input()
                    file.write(info)
                    file.close()

                else:
                    continue

            elif 'new' in query and 'private' in query and 'project' in query:
                speak('working on a secret project sir')
                speak('what should i name it sir')
                query = takeCommand().upper()
                os.chdir('E:\\S.R.I.O.U.S\\PROJECTS')
                os.mkdir(query)
                speak('Creating new file\n')
                speak('Opening the folder')
                os.startfile('E:\\S.R.I.O.U.S\\PROJECTS')

            elif 'atom' in query and 'new excel file' in query:
                speak('Opening new excel file')
                excel_app = "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE"
                os.startfile(excel_app)

            elif 'atom' in query and 'new word file' in query:
                speak('Opening new word file')
                word_app = "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"
                os.startfile(word_app)

            elif 'thanks' in query or 'thank you' in query:
                speak('Anything for you')

            elif 'atom' in query and 'new presentation file' in query:
                speak('Opening presentation file')
                pres_app = "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE"
                os.startfile(pres_app)

            elif 'atom' in query and 'new design file' in query:
                speak('Opening Solidworks')
                solidworks_app = "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\SOLIDWORKS 2016\\SOLIDWORKS 2016 x64 Edition"
                os.startfile(solidworks_app)

            elif 'atom' in query and 'check my mail' in query:
                speak('will do sir')
                speak('Opening your inbox')
                webbrowser.get('firefox').open_new_tab('www.gmail.com')

            elif 'atom' in query and 'open movie folder' in query:
                speak('opening your movie folder')
                os.startfile('D:\\MOVIES')

            elif 'atom' in query and 'open my picture folder' in query:
                speak('on its way sir')
                os.startfile('D:\\PICTURES')

            elif 'see you later' in query or 'good bye' in query or 'see you' in query:
                speak('enjoy yourself sir')
                exit()

            elif 'atom' in query and ('are you up' in query or 'talk to me' in query):
                speak('for you sir, always')

else:
    print("Malfunction")
    exit()
