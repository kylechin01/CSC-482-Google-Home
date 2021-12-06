# Test aspects of the schedules dataframe and related response

import unittest
import sys
sys.path.append('../')

from mainHelpers import *
from schedules_query_processor import *

wikiret = None

# Get DF and related info for schedules
schDf = {}
df_files = glob.glob("../data/*.csv")
for file in df_files:
    df_name = re.split("\\\\|/|\.c", file)[2]
    schDf[df_name] = pd.read_csv(file, encoding="ISO-8859-1")
with open("../data/keywords.json") as json_file:
    schDict = json.load(json_file)

schedulesProcessor = Processor(schDf)

p = Preprocessor(schDict)

class SchedulesTest(unittest.TestCase):

    def test_handleOfficeQuestion(self):
        def testOH(query, expectedTerms):
            qp = p.preprocessAndClassifyQuery(query)
            if qp["classification"] != "schedules":
                self.assertTrue(False) # wrong classification
            resp = schedulesProcessor.getResponse(qp)
            print(f"Given: {query}\nReturn: {resp}\n\n")
            for t in expectedTerms:
                self.assertTrue(t.lower() in resp.lower())

        testOH("Where are Foaad Khosmood's office hours?", ["professor khosmood", "building 14", "room 213"])
        testOH("Where are Amy Carter's office hours?", ["professor carter", "building 3", "room 100"])
        testOH("Where are Amy Carter's office hours?", ["professor carter", "building 3", "room 100"])

    def test_handleClassQuestion(self):
        def testClass(query, expectedTerms):
            qp = p.preprocessAndClassifyQuery(query)
            if qp["classification"] != "schedules":
                self.assertTrue(False) # wrong classification
            resp = schedulesProcessor.getResponse(qp)
            print(f"Given: {query}\nReturn: {resp}\n\n")
            for t in expectedTerms:
                self.assertTrue(t.lower() in resp.lower())

        testClass("When is CSC 482 section 2?", ["MWF", "12:10 PM", "1:00 PM"])
        testClass("What time is CSC 482 section 1?", ["MWF", "11:10 AM", "12:00 PM"])
        testClass("What time is CSC 482 section 03?", ["MWF", "2:10 PM", "3:00 PM"])
        testClass("What time is CSC 482 section 99?", ["could not find"])

        testClass("What classes is Foaad teaching this quarter?", ["11 classes", "CSC", "CPE"])
        testClass("What classes is Foaad teaching next quarter?", ["Winter Quarter 2022", "10 classes"])
        testClass("What classes is Foaad teaching?", ["11 classes", "CSC", "CPE"])
        testClass("What classes is Mammen teaching?", ["0 classes"])

    def test_handleTermQuestions(self):
        def testTerm(query, expectedTerms):
            qp = p.preprocessAndClassifyQuery(query)
            if qp["classification"] != "schedules":
                self.assertTrue(False) # wrong classification
            resp = schedulesProcessor.getResponse(qp)
            print(f"Given: {query}\nReturn: {resp}\n\n")
            for t in expectedTerms:
                self.assertTrue(t.lower() in resp.lower())

        testTerm("When is CSC 480 section 1?", ["starts at 09:40 AM"])
        testTerm("When is CSC 480 section 1 this quarter?", ["starts at 09:40 AM"])
        testTerm("When is CSC 480 section 3 next quarter?", ["Winter Quarter 2022", "starts at 01:40 PM"])
        testTerm("What was the waitlist status of CSC 480 section 3 last quarter?", ["Summer Quarter 2021", "3 on the waitlist"])
        testTerm("When is CSC 480 section 3 Spring 2022?", ["Spring Quarter 2022", "08:10 AM"])
        testTerm("When was CSC 480 section 4 Fall 2022?", ["could not find any term"])
        testTerm("When was CSC 480 section 4 Fall?", ["could not find any term"])

    def test_handleCourseClassQuestions(self):
        def testQ(query, expectedTerms):
            qp = p.preprocessAndClassifyQuery(query)
            if qp["classification"] != "schedules":
                self.assertTrue(False) # wrong classification
            resp = schedulesProcessor.getResponse(qp)
            print(f"Given: {query}\nReturn: {resp}\n\n")
            for t in expectedTerms:
                self.assertTrue(t.lower() in resp.lower())

        testQ("Is CSC 480 offered next quarter?", ["is offered", "4 sections"])
        testQ("Is CSC 482 offered next quarter?", ["CSC 482 is not offered"])
        testQ("What CSC classes are offered next quarter?", ["68", "CSC", "65 others"])
        testQ("What MATH classes are offered next quarter?", ["56", "MATH", "53 others"])

    def test_GEFulfillmentQuestions(self):
        def testQ(query, expectedTerms):
            qp = p.preprocessAndClassifyQuery(query)
            if qp["classification"] != "schedules":
                self.assertTrue(False) # wrong classification
            resp = schedulesProcessor.getResponse(qp)
            print(f"Given: {query}\nReturn: {resp}\n\n")
            for t in expectedTerms:
                self.assertTrue(t.lower() in resp.lower())

        testQ("A1 GE?", ["3 courses"])
        testQ("C1 GE?", ["21 courses", "18 others"])
        testQ("F1 GE?", ["no courses"])
        testQ("C1 ARCH GE?", ["1 ARCH course"])
        testQ("C1 MATH GE?", ["no MATH courses"])

    def test_handleNameOfCourseQuestion(self):
        def testQ(query, expectedTerms):
            qp = p.preprocessAndClassifyQuery(query)
            if qp["classification"] != "schedules":
                self.assertTrue(False) # wrong classification
            resp = schedulesProcessor.getResponse(qp)
            print(f"Given: {query}\nReturn: {resp}\n\n")
            for t in expectedTerms:
                self.assertTrue(t.lower() in resp.lower())
        
        testQ("What is the name of CSC 482", ["speech and language processing", "CSC", "482"])
        testQ("What is the name of CPE 202", ["CPE", "202", "data structures"])
        testQ("What is the name of XXX 101", [""]) # Should fail
        testQ("What is the name of COMS 101", ["COMS", "101", "public speaking", "A1"])
        testQ("What GE does COMS 101 satisfy", ["COMS", "101", "public speaking", "A1"])
    
    def test_noProfInitials(self):
        # make sure there are no single letter professor keywords
        for p in schDict["instructor_names"]:
            if len(p) <= 1:
                print(p)
                self.assertTrue(False)
