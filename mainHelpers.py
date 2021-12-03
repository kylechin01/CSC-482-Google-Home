
from wikipedia import webscrapeWikipedia, getResponse, getDF
from classification import Preprocessor
import json
import glob
import pandas as pd

def initMain():
    """
    Initializes all data needed for the main function including
    preprocessing, schedules, and wikipedia related objects
    """
    if True: # TODO: have a condition so it only webscrapes when needed
        completeWebscrape()

    # Get DF and related info for wikipedia
    wikiRet = getDF()

    # Get DF and related info for schedules
    schDf = []
    df_files = glob.glob("data/*.csv")
    for file in df_files:
        schDf.append(tuple([file, pd.read_csv(file, encoding="ISO-8859-1")]))
    with open("data/keywords.json") as json_file:
        schDict = json.load(json_file)

    # initialize objects and variables
    p = Preprocessor(schDict)

    return p, wikiRet, schDf

def getQuery():
    # TODO: temp, feel free to remove and change
    return "What is the average GPA?"

def handleSchedulesQuery(qp, schDf):
    print(qp["cats"])
    return "WIP"

def answerQuery(resp):
    # TODO: temp, feel free to remove and change
    print(resp)

def completeWebscrape():
    webscrapeWikipedia()
    # TODO webscrape schedules

def handleQuery(query, p, schDf, wikiRet):
    qp = p.preprocessAndClassifyQuery(query)
    if qp["classification"] == "schedules":
        resp = handleSchedulesQuery(qp, schDf)
    elif qp["classification"] == "wikipedia":
        resp = getResponse(wikiRet[0], wikiRet[1], wikiRet[2], qp["strQuery"])