# Tests the integration of multiple parts of the project

import unittest
import sys
sys.path.append('../')

from main import *

class IntegrationTest(unittest.TestCase):
    def test_integrate_wiki(self):
        # init stuff
        completeWebscrape()
        wikiRet = getDF()

        schDict = {
            "instructor": {"Foaad", "Khosmood", "Franz", "Kurfess"},
            "time": {"spring", "winter", "fall", "summer", "next", "last"},
            "department": {"CSC", "college of engineering", "computer science"},
            "course": {"natural language processing", r"[0-9][0-9][0-9]"}
        } # classifications and associated word lists
        p = Preprocessor(schDict)
        
        
        def thq(query, expectedTerms):
            resp = handleQuery(query, p, wikiRet)
            for t in expectedTerms:
                self.assertTrue(t.lower() in resp.lower())
            print(f"Given: {query}\nReturn: {resp}\n\n")
        
        thq("Who is the president of cal poly?", ["Armstrong"])
        thq("What is the average gpa of cal poly students?", ["gpa"])
        # thq("What is the cal poly orientation like?", ["orientation"])
        # thq("Does cal poly offer tutoring services?", ["services"])
        # thq("Does cal poly offer financial aid?", ["aid"])
        # thq("How much does it cost to go to cal poly?", [""]) # Not performing well
        # thq("What is the ratio of students to professors?", [""]) # Not performing well
        # thq("What is the student faculty ratio?", [""]) # Not performing well


        #thq("What classes does professor foaad teach next quarter?", ["Schedules", "implemented"]) # temp
        # TODO


def handleQuery(query, p, wikiRet):
    """
    Psuedo main
    """
    qp = p.preprocessAndClassifyQuery(query)
    if qp["classification"] == "schedules":
        resp = handleSchedulesQuery(qp, {})
    elif qp["classification"] == "wikipedia":
        resp = getResponse(wikiRet[0], wikiRet[1], wikiRet[2], qp["strQuery"])
    return resp