
from classification import Preprocessor

def main():
    # webscraping
    # TODO
    schDf = []
    wikiDf = []
    schDict = {} # classifications and associated word lists

    # initialize objects and variables
    p = Preprocessor(schDict)

    mainLoop(p, schDf, wikiDf)

def mainLoop(p, schDf, wikiDf):
    while True:
        query = getQuery()
        qp = p.preprocessAndClassifyQuery(query)
        if qp["classification"] == "schedules":
            resp = handleSchedulesQuery(qp, schDf)
        elif qp["classification"] == "wikipedia":
            resp = handleWikipediaQuery(qp, wikiDf)
        answerQuery(resp)
        
def getQuery():
    # TODO: temp, feel free to remove and change
    pass

def handleSchedulesQuery(qp, schDf):
    # TODO: temp, feel free to remove and change
    pass

def handleWikipediaQuery(qp, wikiDf):
    # TODO: temp, feel free to remove and change
    pass

def answerQuery(resp):
    # TODO: temp, feel free to remove and change
    pass

if __name__ == '__main__':
    main()