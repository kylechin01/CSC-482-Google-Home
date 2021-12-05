
from wikipedia import webscrapeWikipedia, getResponse, getDF
from schedules_query_processor import Processor
from classification import Preprocessor
import json
import glob
import pandas as pd
import re

def initMain():
    """
    Initializes all data needed for the main function including
    preprocessing, schedules, and wikipedia related objects
    """
    if False: # TODO: have a condition so it only webscrapes when needed
        completeWebscrape()

    # Get DF and related info for wikipedia
    wikiRet = getDF()

    # Get DF and related info for schedules
    schDf = {}
    df_files = glob.glob("data/*.csv")
    for file in df_files:
        df_name = re.split("\\\\|/|\.", file)[1]
        schDf[df_name] = pd.read_csv(file, encoding="ISO-8859-1")
    with open("data/keywords.json") as json_file:
        schDict = json.load(json_file)

    # initialize objects and variables
    p = Preprocessor(schDict)
    schedulesProcessor = Processor(schDf)

    return p, wikiRet, schedulesProcessor

def completeWebscrape():
    webscrapeWikipedia()
    # TODO webscrape schedules

def handleQuery(query, p, schP, wikiRet):
    qp = p.preprocessAndClassifyQuery(query)
    resp = ""
    if qp["classification"] == "schedules":
        resp = schP.getResponse(qp)
        if resp == "":
            resp = getResponse(wikiRet[0], wikiRet[1], wikiRet[2], qp)
    elif qp["classification"] == "wikipedia":
        resp = getResponse(wikiRet[0], wikiRet[1], wikiRet[2], qp)
        if resp == "":
            resp = schP.getResponse(qp)
    if resp == "":
        resp = "Sorry I don't know how to respond to that."
    return resp
