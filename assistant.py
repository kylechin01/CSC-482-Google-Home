import argparse
import locale
import logging

from aiy.board import Board, Led
from aiy.cloudspeech import CloudSpeechClient
import aiy.voice.tts
import json
from mainHelpers import initMain, handleQuery

def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Assistant service example.')
    parser.add_argument('--language', default=locale_language())
    args = parser.parse_args()

    logging.info('Initializing for language %s...', args.language)
    hints = get_hints(args.language)
    client = CloudSpeechClient()

    p, wikiRet, schDf = initMain()
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
            text = text.lower()
            if 'turn on the light' in text:
                board.led.state = Led.ON
            elif 'turn off the light' in text:
                board.led.state = Led.OFF
            elif 'blink the light' in text:
                board.led.state = Led.BLINK
            elif 'repeat after me' in text:
                to_repeat = text.replace('repeat after me', '', 1)
                aiy.voice.tts.say(to_repeat)
            elif 'variation mode' in text:
                get_variations(client, args)
            elif 'goodbye' in text:
                break
            else:
                resp = handleQuery(text, p, schDf, wikiRet)
                aiy.voice.tts.say(resp)
                

def get_hints(language_code):
    if language_code.startswith('en_'):
        hints = ['turn on the light',
                'turn off the light',
                'blink the light',
                'goodbye',
		'repeat after me', 'foaad khosmood', 'variation mode']
        f = open('./data/keywords.json')
        data = json.load(f)
        #for key in data.keys():
        #    for val in data[key]:
        #        hints.append(str(val))
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

    logging.info(variations)


if __name__ == '__main__':
    main()
