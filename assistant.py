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
    prof_dict = {('broadcast', 'foad', 'costumes', 'flood', 'mode','cashman', 'cushman', 'ford', 'cosmid', 'koch', 'vodka', 'shmood','crash', 'harshman','broadcast', 'moon', 'akash', 'cosman', 'crossword', 'kush'):'Foaad Khosmood' }
    tok_text = text.split(" ")
    for tok in tok_text:
        for key in prof_dict.keys():
            if tok in key or tok in [word.capitalize() for word in key]:
                if tok == 'crash' and 'plane' in tok_text:
                    text = text
                else:
                    text = text.replace(tok, prof_dict[key], 1)
    return text

def apply_edge_rules_ques(text):
    # CSE -> CSC
    def helpSwap(opts, res, text):
        for opt in opts:
            if opt in text.lower():
                text = text.replace(opt, res, 1)
                text = text.replace(opt.upper(), res, 1)
        return text
    
    text = helpSwap(["cse", "tsc", "cic","clc", "esc", "cfe", "cfd", "coc", "csce", "scsc", "cfc", "vsc", "csv"], "CSC", text)
    #if "cse" in text.lower():
    #    text = text.replace('CSE', 'CSC', 1)
    #elif "tsc" in text.lower():
    #    text = text.replace('tsc', 'CSC', 1)
    #    text = text.replace('TSC', 'CSC', 1)
    #elif "cic" in text.lower():
    #    text = text.replace('cic', 'CSC', 1)
    #    text = text.replace('CIC', 'CSC', 1)
    #elif "cfc" in text.lower():
    #    text = text.replace('cfc', 'CSC', 1)
    #    text = text.replace('CFC', 'CSC', 1)
    #elif "vsc" in text.lower():
    #    text = text.replace('vsc', 'CSC', 1)
    #    text = text.replace('VSC', 'CSC', 1)
    #elif "csv" in text.lower():
    #    text = text.replace('csv', 'CSC', 1)
    #    text = text.replace('CSV', 'CSC', 1)
    
    
    #exporter -> next quarter
    if 'exporter' in text.lower():
        text = text.replace('exporter', 'next quarter')
        text = text.replace('Exporter', 'next quarter')
        text = text.replace('EXPORTER', 'next quarter')
    # math-> MATH 
    if "math" in text.lower():
        text = text.replace('math', 'MATH', 1)
        text = text.replace('Math', 'MATH', 1)
    # engl-> ENGL 
    if " art " in text.lower():
        text = text.replace('engl', 'ENGL', 1)
        text = text.replace('Engl', 'ENGL', 1)

    # art -> ART
    if " art " in text.lower():
        text = text.replace('art', 'ART', 1)
        text = text.replace('Art', 'ART', 1)
    # arch -> ARCH
    if "arch" in text.lower():
        text = text.replace('arch', 'ARCH', 1)
        text = text.replace('Arch', 'ARCH', 1)
    # comms -> COMS
    if "comms" in text.lower():
        text = text.replace('comms', 'COMS', 1)
        text = text.replace('COMMS', 'COMS', 1)
    # emmy -> ME
    if "emmy" in text.lower():
        text = text.replace('emmy', 'ME', 1)
        text = text.replace('Emmy', 'ME', 1)
        text = text.replace('emmys', 'ME', 1)
        text = text.replace('Emmys', 'ME', 1)
        text = text.replace('EMMY', 'ME', 1)
    # bus -> BUS
    if "bus" in text.lower():
        text = text.replace('bus', 'BUS', 1)
        text = text.replace('Bus', 'BUS', 1)

    # african american -> black
    if "african" in text.lower():
        text = text.replace('african', 'black', 1)
        text = text.replace('African', 'black', 1)
    # mascot -> mascots for the wikipedia section
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
    elif "MTWF" in text:
        text = text.replace('MTWF', 'Monday, Tuesday, Wednesday and Friday', 1)
    elif "MWRF" in text:
        text = text.replace('MWRF', 'Monday, Wednesday, Thursday and Friday', 1)
    elif "MW" in text:
        text = text.replace('MW', 'Monday and Wednesday', 1)
    # ex 1.0 -> 1
    if ".0" in text:
        text = text.replace('.0', '', 1)
    return text


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Assistant service example.')
    parser.add_argument('--language', default=locale_language())
    args = parser.parse_args()

    # logging.info('Initializing for language %s...', args.language)
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
                #logging.info('You said nothing.')
                aiy.voice.tts.say('Please repeat that?')
                continue

            #logging.info('You said: "%s"' % text)
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
                aiy.voice.tts.say("Goodbye!")
                break
            elif 'hello' in text.lower():
                aiy.voice.tts.say("How may I help you today?")
            else:
                if len(text.split(' ')) == 1 or len(text.split(' ')) == 2 :
                    print('Q: '+text)
                    answer ="Sorry I don't know how to respond to that."
                    print('A: '+answer)
                    aiy.voice.tts.say(answer)
                    continue
                new_text = apply_edge_rules_ques(text)
                print('Q: '+new_text)
                answer = send_query(apply_edge_rules_ques(text))
                new_answer = apply_edge_rules_resp(answer)
                print('A: '+new_answer)
                aiy.voice.tts.say(new_answer)

if __name__ == '__main__':
    main()
