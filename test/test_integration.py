# Tests the integration of multiple parts of the project

import unittest
import sys
sys.path.append('../')

from mainHelpers import *

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
        
        
        def thq(query, expectedTerms=[""]):
            resp = handleQuery(query, p, {}, wikiRet)
            for t in expectedTerms:
                self.assertTrue(t.lower() in resp.lower())
            print(f"Given: {query}\nReturn: {resp}\n\n")
        
        thq("Who is the president of cal poly?", ["Armstrong"])
        thq("What is the average gpa of cal poly students?", [""])
        thq("What is the cal poly orientation like?", ["orientation"])
        thq("Does cal poly offer tutoring services?", [""])
        thq("Does cal poly offer financial aid?", ["aid"])
        thq("What kind of clubs does cal poly have?", [""])
        thq("How many students attend cal poly?", [""])
        thq("What percent of students are Hispanic?", [""])
        thq("What is the greek life like at cal poly?", [""])

        thq("How much does it cost to go to cal poly?", [""])
        thq("What is the ratio of students to professors?", [""])
        thq("What is the student faculty ratio?", [""])
        thq("What majors does cal poly offer?", [""])
        thq("How many colleges are in Cal Poly?", [""])

        thq("wefoji; whofi;a uiafsl")
        thq("Is the sky blue")
        thq("Does God exist?")
        thq("Tell me about best water bottle")
        thq("Did Google create a voice kit?")
        thq("How are you?")

        thq("What percent of females are at Cal Poly?")
        thq("What is the percentage of Asians?")