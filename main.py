# -*- coding: utf-8 -*-
# noinspection PyPackageRequirements
from PIL import Image, ImageDraw
import requests
from lxml import html
import time
import argparse
import pyttsx
import speech_recognition as sr
import sys
import cv2
import base64
from googleapiclient.discovery import build
import httplib2
import logging
import random
import string
import urllib
import winsound


class GoogleCloudVisionClient:
    __base64_image = ''
    __url = 'https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'
    __service = None
    __max_results = 1
    __filename = ''

    def __init__(self, _key, _max_results):
        self.__service = build('vision', 'v1', httplib2.Http(), discoveryServiceUrl=self.__url, developerKey=_key)
        self.__max_results = _max_results

    def get_batch_request(self, _content, _type):
        return {'requests': [{
            'image': {'content': _content},
            'features': [{'type': _type, 'maxResults': self.__max_results}]
        }]}

    @staticmethod
    def encode_image(image):
        """
        Pass the image data to an encoding function
        :param image:
         :return:
        """
        image_content = image.read()
        return base64.b64encode(image_content)

    def make_detection(self, _type):
        batch_request = self.get_batch_request(self.__base64_image, _type)
        request = self.__service.images().annotate(body=batch_request)
        response = request.execute()
        return response

    def highlight_faces(self, faces, output_filename):
        """Draws a polygon around the faces, then saves to output_filename.

        Args:
          faces: a list of faces found in the file. This should be in the format
              returned by the Vision API.
          output_filename: the name of the image file to be created, where the faces
              have polygons drawn around them.
        """
        im = Image.open(self.__filename)
        draw = ImageDraw.Draw(im)

        for face in faces:
            box = [(v['x'], v['y']) for v in face['fdBoundingPoly']['vertices']]
            draw.line(box + [box[0]], width=5, fill='#00ff00')

        del draw
        im.save(output_filename)

    def init_image(self, _filename):
        self.__filename = _filename
        with open(_filename, 'rb') as image_file:
            self.__base64_image = self.encode_image(image_file)

    def cam_cap_label(self):
        """
        Takes Camera capture. And then detect labels on it
        :return:
        """
        # noinspection PyArgumentList
        cam = cv2.VideoCapture(0)
        ret, img = cam.read()
        cnt = cv2.imencode('.png', img)[1]
        self.__base64_image = base64.b64encode(cnt)
        cam.release()

        res = w.make_detection('LABEL_DETECTION')
        if res['responses'][0]:
            return ', '.join([t['description'].strip() for t in res['responses'][0]['labelAnnotations']]).strip()
        else:
            return 'Labels not detected'


class ChatBotClient:
    __url = ''
    __client_name = 'You'
    __bot_name = 'Mitsuku'
    __engine = None

    def __init__(self, _url, _nuance_app_id, _nuance_app_key, _nuance_tts_uri, _nuance_tts_endpoint,
                 _client_name='You', _bot_name='Mitsuku'):
        self.__url = _url
        self.__client_name = _client_name
        self.__bot_name = _bot_name
        self.__engine = pyttsx.init()
        self.__engine.setProperty('rate', 120)
        voices = self.__engine.getProperty('voices')
        # noinspection SpellCheckingInspection
        voice = [v for v in voices if u'Microsoft Zira Desktop - English (United States)' == v.name][0]
        self.__engine.setProperty('voice', voice.id)
        self.nuance_app_id = _nuance_app_id
        self.nuance_app_key = _nuance_app_key
        self.nuance_tts_uri = _nuance_tts_uri
        self.nuance_tts_endpoint = _nuance_tts_endpoint
        self.nuance_tts_lang = 'en_US'
        self.nuance_voice = 'Susan'
        self.nuance_id = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(8)])

    def send(self, _message):
        resp = requests.post(self.__url, data={'message': _message})
        tree = html.fromstring(resp.text)
        line = tree.xpath('./body/p/font/*')
        answer = line[2].tail
        print '%s:%s' % (self.__bot_name, answer)
        # self.__engine.say(answer)
        # self.__engine.runAndWait()

        nuance_tts_headers = {"Content-Type": "text/plain", "Accept": "audio/x-wav"}
        nuance_tts_params = urllib.urlencode({
            'appId': self.nuance_app_id, 'appKey': self.nuance_app_key, 'id': self.nuance_id,
            'ttsLang': self.nuance_tts_lang, 'voice': self.nuance_voice})
        nuance_tts_url = '%s%s?%s' % (self.nuance_tts_uri, self.nuance_tts_endpoint, nuance_tts_params)
        nuance_tts_req = requests.post(nuance_tts_url, data=answer, headers=nuance_tts_headers)
        winsound.PlaySound(nuance_tts_req.content, winsound.SND_MEMORY)


if __name__ == '__main__':
    logging.basicConfig(filename='debug.log', level=logging.DEBUG)
    logger = logging.getLogger('chat_bot')
    r = sr.Recognizer()

    p = argparse.ArgumentParser()
    p.add_argument('-m', dest='message', help='your message')
    p.add_argument('-s', dest='input_source', help='type or voice', default='type')
    p.add_argument('-i', dest='image_file', help='The image you\'d like to label.', default='image.jpg')
    p.add_argument("-k", dest='google_api_key', help='Google Cloud Vision API key', required=True)
    p.add_argument('--max-results', help='Google Cloud Vision max-results', default=1)
    p.add_argument('--nuance-app-id', help='Nuance App Id')
    p.add_argument('--nuance-app-key', help='Nuance App Key')
    p.add_argument('--nuance-tts-uri', help='Nuance TTS URI')
    p.add_argument('--nuance-tts-endpoint', help='Nuance TTS Endpoint')
    p.add_argument('--nuance-asr-uri', help='Nuance ASR URI')
    p.add_argument('--nuance-asr-endpoint', help='Nuance ASR Endpoint')
    args = p.parse_args()

    client_name = 'You'
    # noinspection SpellCheckingInspection
    url = 'http://fiddle.pandorabots.com/pandora/talk?botid=9fa364f2fe345a10&skin=demochat'
    client = ChatBotClient(url, args.nuance_app_id, args.nuance_app_key, args.nuance_tts_uri,
                           args.nuance_tts_endpoint, client_name, 'Mitsuku')

    if args.input_source not in ['type', 'voice']:
        print 'Wrong parameter value %s for input_source parameter' % args.input_source
        sys.exit(1)
    if args.message:
        print '%s: %s' % (client_name, args.message)
        client.send(args.message)
    else:
        if 'type' == args.input_source:
            print 'Type ''Bye''<Enter> to exit. Type ''Look at me'' to look at me'
        else:
            print 'Say ''Bye'' to exit. Say ''Look at me'' to look at me'

        while True:
            if 'type' == args.input_source:
                message = raw_input('You (type something): ')
            elif 'voice' == args.input_source:
                # while True:
                #     with sr.Microphone() as source:
                #         r.adjust_for_ambient_noise(source)
                #         print 'You (say something):',
                #         audio = r.listen(source)
                #     randomID = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(8)])
                #
                #     # HTTP Request Headers
                #     nuance_asr_headers = {
                #         "Content-Type": "audio/x-wav;codec=pcm;bit=16;rate=8000",
                #         "Content-Length": len(audio.get_wav_data()),
                #         "Accept": "text/plain",
                #         "Accept-Topic": "Dictation",
                #         "Accept-Language": "en-US"
                #     }
                #
                #     nuance_asr_params = urllib.urlencode({'appId': args.nuance_app_id,
                #                                           'appKey': args.nuance_app_key, 'id': randomID})
                #     nuance_asr_url = '%s%s?%s' % (args.nuance_asr_uri, args.nuance_asr_endpoint, nuance_asr_params)
                #     nuance_asr_req = requests.post(nuance_asr_url, data=audio.get_wav_data(),
                #                                    headers=nuance_asr_headers)
                #     if 200 == nuance_asr_req.status_code:
                #         message = nuance_asr_req.text.strip().replace('\n', ', ')
                #         print message
                #         break
                #     else:
                #         print 'Please repeat'
                #         continue

                while True:
                    with sr.Microphone() as source:
                        r.adjust_for_ambient_noise(source)
                        print 'You (say something):',
                        audio = r.listen(source)
                    try:
                        # for testing purposes, we're just using the default API key to use another API key, use
                        # `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                        # instead of `r.recognize_google(audio)`
                        message = r.recognize_google(audio)
                        print message
                        break
                    except sr.UnknownValueError:
                        print("Google Speech Recognition could not understand audio. Please repeat")
                        continue
                    except sr.RequestError as e:
                        print("Could not request results from Google Speech Recognition service; {0}".format(e))
                        sys.exit(1)

            if 'bye' == message.lower():
                break
            elif 'look at me' == message.lower():
                w = GoogleCloudVisionClient(args.google_api_key, args.max_results)
                labels = w.cam_cap_label()
                logger.debug('Recognized labels: %s' % labels)
                msg = 'I am a %s' % labels
                client.send(msg)
            else:
                client.send(message)
            time.sleep(.3)
