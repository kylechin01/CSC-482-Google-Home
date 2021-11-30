
from classification import Preprocessor
from wikipedia import webscrapeWikipedia, getResponse, getDF

def main():
    # webscraping
    if True: # TODO: have a condition so it only webscrapes when needed
        completeWebscrape()
    # TODO

    # Get DF and related info for wikipedia
    wikiRet = getDF()

    # Get DF and related info for schedules
    schDf = []
    schDict = {} # classifications and associated word lists

    # initialize objects and variables
    p = Preprocessor(schDict)

    mainLoop(p, schDf, wikiRet)

def mainLoop(p, schDf, wikiRet):
    while True:
        query = getQuery()
        qp = p.preprocessAndClassifyQuery(query)
        if qp["classification"] == "schedules":
            resp = handleSchedulesQuery(qp, schDf)
        elif qp["classification"] == "wikipedia":
            resp = getResponse(wikiRet[0], wikiRet[1], wikiRet[2], qp["strQuery"])
        answerQuery(resp)
        break # TODO: delete
        
def getQuery():
    # TODO: temp, feel free to remove and change
    return "What is the average GPA?"

def handleSchedulesQuery(qp, schDf):
    # TODO: temp, feel free to remove and change
    return "Schedules has yet to be implemented..."

# def handleWikipediaQuery(qp, wikiRet):
#     resp = getResponse(wikiRet[0], wikiRet[1], wikiRet[2], qp["strQuery"])
#     return resp

def answerQuery(resp):
    # TODO: temp, feel free to remove and change
    print(resp)

def completeWebscrape():
    webscrapeWikipedia()
    # TODO webscrape schedules

if __name__ == '__main__':
    main()