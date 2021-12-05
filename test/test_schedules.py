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
    df_name = re.split("\\\\|/|\.", file)[1]
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

    def test_handleNameOfCourseQuestion(self):
        pass