import random
import requests
import urllib.parse
import json
import os
import sys
from urllib.request import urlopen
from pydub import AudioSegment
from pydub.playback import play
import pytchat

_NonceEndpoint = "https://acapelavoices.acapela-group.com/index/getnonce/"
_SynthesizerEndpoint = "https://www.acapela-group.com:8443/Services/Synthesizer"
_CachedNonce = ""
_CachedEmail = ""
_LastFailed = False
voices = ["enu_willfromafar_22k_ns.bvcu", "eng_queenelizabeth_22k_ns.bvcu", "eng_peterhappy_22k_ns.bvcu", "enu_willoldman_22k_ns.bvcu"]

def get_sound_link(text, voiceid):
    _CachedNonce = ""
    _CachedEmail = ""
    _LastFailed = ""

    email_length = random.randint(10, 20)
    fake_email = ''.join(chr(random.randint(1, 26) + 64) for _ in range(email_length)) + "@gmail.com"

    nonce_request_values = {
        "json": json.dumps({"googleid": fake_email})
    }

    nonce_response = requests.post(_NonceEndpoint, data=nonce_request_values).text
    nonce_trimmed = nonce_response[len('{"nonce":"'):]
    nonce_trimmed = nonce_trimmed[:-2]
    _CachedNonce = nonce_trimmed
    _CachedEmail = fake_email

    synthesizer_request_string = f"req_voice={voiceid}&cl_pwd=&cl_vers=1-30&req_echo=ON&cl_login=AcapelaGroup&req_comment=%7B%22nonce%22%3A%22{_CachedNonce}%22%2C%22user%22%3A%22ballchewer@gmail.com%22%7D&req_text={urllib.parse.quote(text)}&cl_env=ACAPELA_VOICES&prot_vers=2&cl_app=AcapelaGroup_WebDemo_Android"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    synthesizer_response = requests.post(_SynthesizerEndpoint, headers=headers, data=synthesizer_request_string)

    if synthesizer_response.status_code != 200:
        _LastFailed = True
        return ""

    synthesizer_response_string = synthesizer_response.text
    synthesizer_respone_url = synthesizer_response_string[synthesizer_response_string.find("https://"):synthesizer_response_string.find(".mp3") + len(".mp3")]

    _LastFailed = True
    return synthesizer_respone_url

def play_sound(text, voiceid):
    mp3file = urlopen(get_sound_link(text, voiceid))
    with open('./tts.mp3','wb') as output:
      output.write(mp3file.read())
    song = AudioSegment.from_mp3("./tts.mp3")
    play(song)
    os.remove("./tts.mp3")

chat = pytchat.create(video_id=sys.argv[1])
while chat.is_alive():
    for c in chat.get().sync_items():
        play_sound(c.message, random.choice(voices))
