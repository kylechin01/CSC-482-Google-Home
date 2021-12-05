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

        testClass("What classes is Foaad teaching this quarter?", ["14 classes", "CSC", "CPE"])
        testClass("What classes is Foaad teaching next quarter?", ["lorem"])
        testClass("What classes is Foaad teaching?", ["14 classes", "CSC", "CPE"])
        testClass("What classes is Mammen teaching?", ["0 classes"])

    def test_handleNameOfCourseQuestion(self):
        pass