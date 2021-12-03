from wikipedia import getResponse, getDF
from mainHelpers import initMain, getQuery, handleSchedulesQuery,\
    answerQuery, handleQuery

def main():
    p, schDf, wikiRet = initMain()

    mainLoop(p, schDf, wikiRet)

def mainLoop(p, schDf, wikiRet):
    while True:
        query = getQuery()
        resp = handleQuery(query)
        answerQuery(resp)
        break # TODO: delete

if __name__ == '__main__':
    main()