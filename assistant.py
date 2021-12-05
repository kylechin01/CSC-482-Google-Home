import argparse
import locale
import logging

from aiy.board import Board, Led
from aiy.cloudspeech import CloudSpeechClient
import aiy.voice.tts
import json
import requests


def get_hints(language_code):
    if language_code.startswith('en_'):
        hints = ['turn on the light',
                'turn off the light',
                'blink the light',
                'goodbye',
		'repeat after me', 'variation mode']
        f = open('./data/keywords.json')
        data = json.load(f)
        for val in data['instructor_names']:
            hints.append(str(val))
        f.close()
        return list(set(hints))
    return None

def locale_language():
    language, _ = locale.getdefaultlocale()
    return language

def get_variations(client, args):
    variations = []
    logging.info('Say the tricky word that you need to make rules for')
    while True:
        logging.info('Say "end now" when done')
        text = client.recognize(language_code=args.language)
        if text is not None:
            if 'end now' in text:
                break
            text = text.lower()
            variations.append(text)

    logging.info(list(set(variations)))

def get_flask_stuff():
    resp = requests.get('http://192.168.43.3:5000/')
    return resp.text

def send_query(text):
    resp = requests.get('http://192.168.43.3:5000/query/'+text)
    return resp.text

def handle_prof_names(text):
    prof_dict = {('broadcast', 'mode', 'cushman', 'ford', 'cosmid', 'koch', 'vodka', 'shmood','crash', 'harshman','broadcast', 'moon', 'akash', 'cosman', 'crossword', 'kush'):'Foaad Khosmood' }
    tok_text = text.split(" ")
    for tok in tok_text:
        for key in prof_dict.keys():
            if tok in key or tok in [word.capitalize() for word in key]:
                text = text.replace(tok, prof_dict[key], 1)
    return text

def apply_edge_rules_ques(text):
    # CSE -> CSC
    if "cse" in text.lower():
        text = text.replace('cse', 'CSC', 1)
        text = text.replace('CSE', 'CSC', 1)
    # comms -> COMS
    if "comms" in text.lower():
        text = text.replace('comms', 'COMS', 1)
        text = text.replace('COMMS', 'COMS', 1)
    # emmy -> ME
    if "emmy" in text.lower():
        text = text.replace('emmy', 'ME', 1)
        text = text.replace('EMMY', 'ME', 1)
    # african american -> black
    if "african american" in text.lower():
        text = text.replace('african american', 'black', 1)
        text = text.replace('African American', 'black', 1)
    if "mascot" in text.lower():
        text = text.replace('mascot', 'mascots', 1)
        text = text.replace('Mascot', 'mascots', 1)
    # handle professors
    text = handle_prof_names(text)

    return text
def apply_edge_rules_resp(text):
    # MWF
    if "MWF" in text:
        text = text.replace('MWF', 'Monday, Wednesday and Friday', 1)
    elif "TR" in text:
        text = text.replace('TR', 'Tuesday and Thursday', 1)
    # 1.0 -> 1
    if ".0" in text:
        text = text.replace('.0', '', 1)
    return text


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Assistant service example.')
    parser.add_argument('--language', default=locale_language())
    args = parser.parse_args()

    logging.info('Initializing for language %s...', args.language)
    hints = get_hints(args.language)
    client = CloudSpeechClient()
    with Board() as board:
        board.led.state = Led.ON
        while True:
            #if hints:
            #    logging.info('Say something, e.g. %s.' % ', '.join(hints))
            #else:
            logging.info('Say something.')
            text = client.recognize(language_code=args.language,
                                    hint_phrases=hints)
            if text is None:
                logging.info('You said nothing.')
                aiy.voice.tts.say('Could you repeat that?')
                continue

            logging.info('You said: "%s"' % text)
            #text = text.lower()
            if 'turn on the light' in text.lower():
                board.led.state = Led.ON
            elif 'turn off the light' in text.lower():
                board.led.state = Led.OFF
            elif 'blink the light' in text.lower():
                board.led.state = Led.BLINK
            elif 'repeat after me' in text.lower():
                to_repeat = text.replace('repeat after me', '', 1)
                aiy.voice.tts.say(to_repeat)
            elif 'variation mode' in text.lower():
                get_variations(client, args)
            elif 'goodbye' in text:
                break
            elif 'hello' in text.lower():
                aiy.voice.tts.say("How may I help you today?")
            else:
                new_text = apply_edge_rules_ques(text)
                print('Q: '+new_text)
                answer = send_query(apply_edge_rules_ques(text))
                new_answer = apply_edge_rules_resp(answer)
                print('A: '+new_answer)
                aiy.voice.tts.say(new_answer)

if __name__ == '__main__':
    main()
