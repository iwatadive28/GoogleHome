# -*- coding: utf-8 -*-
import os
from pathlib import Path
from bottle import Bottle, request, template, static_file
from gtts import gTTS
import pychromecast

BASE_DIR = Path(__file__).parent
TALK_DIR = BASE_DIR / 'var'
app = Bottle()

@app.route('/talks/<file_path:path>')
def post_talk(file_path):
    return static_file(file_path, root=TALK_DIR)

@app.route("/")
def hello():
    return "Hello World"
    # [/index]へアクセスがあった場合に「html.index」を返す

@app.route('/form', method='GET')
def get_talk_form():
    content = BASE_DIR / 'template.html'
    text = request.forms.text or ''
    lang = request.forms.lang or 'ja'
    return template(content.open().read(), lang=lang, text=text)


@app.route('/form', method='POST')
def post_talk_form():
    text = request.forms.text
    lang = 'ja'
    text_token = generate_talk(text, lang)
    url = f"http://{app.host}:{app.port}/talks/{text_token}"
    # 名前が"リビングルーム"のデバイスを探す
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=["リビングルーム"])
    cast = chromecasts[0]
    mc = cast.media_controller
    print(url)
    cast.wait()
    mc.play_media(url, 'audio/mp3')
    # Shut down discovery
    pychromecast.discovery.stop_discovery(browser)

    return get_talk_form()

def generate_talk(text_form, lang='ja'):
    # text_token = hashlib.sha256((lang + text).encode()).hexdigest()
    text_token = 'test.mp3'
    talk_path = TALK_DIR / text_token
    if os.path.exists(talk_path):
        os.remove(talk_path)

    print(text_form + ',' + lang)
    tts = gTTS(text=str(text_form), lang=lang)
    # tts = gTTS(text='こんにちは', lang='ja')
    tts.save(talk_path)
    return text_token

if __name__ == '__main__':
    if not TALK_DIR.exists():
        TALK_DIR.mkdir()
    app.host = os.environ.get('SERVER_HOST', '192.168.1.17')
    app.port = os.environ.get('SERVER_PORT', '8080')
    app.run(host=app.host, port=app.port, reloader=True)