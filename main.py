from wikipedia import getResponse, getDF
from mainHelpers import initMain, getQuery, answerQuery, handleQuery

def main():
    p, wikiRet, schP = initMain()

    mainLoop(p, schP, wikiRet)

def mainLoop(p, schP, wikiRet):
    while True:
        query = getQuery()
        resp = handleQuery(query, p, schP, wikiRet)
        answerQuery(resp)
        break # TODO: delete

if __name__ == '__main__':
    main()