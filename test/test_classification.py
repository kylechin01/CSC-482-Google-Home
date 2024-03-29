# Tests functions in classification.py including preprocessing

import unittest
import sys
sys.path.append('../')
import json

from classification import *

with open("../data/keywords.json") as json_file:
    officialSchDict = json.load(json_file)

class ClassificationTest(unittest.TestCase):

    def test_preprocessing(self):
        t1 = "This is definitely a sentence."
        p = Preprocessor({})

        d = p.preprocess(t1)
        self.assertEqual(d["strQuery"], t1)
        self.assertEqual(d["tokQuery"], ["This", "is", "definitely", "a", "sentence", "."])
        self.assertEqual(d["meta"].iloc[0]["token"], "This")
        self.assertEqual(d["meta"].iloc[0]["pos"], "PRON")
        self.assertEqual(d["meta"].iloc[0]["lemma"], "this")
        self.assertEqual(d["meta"].iloc[0]["alpha"], True)
        self.assertEqual(d["meta"].iloc[0]["stop"], True)

        t2 = "This is definitely a sentence. Also this is a sentence."
        d = p.preprocess(t2)
        self.assertEqual(d["strQuery"], t2)
        self.assertEqual(d["tokQuery"], ["This", "is", "definitely", "a", "sentence", ".", "Also", "this", "is", "a", "sentence", "."])
        self.assertEqual(d["meta"].iloc[2]["token"], "definitely")
        self.assertEqual(d["meta"].iloc[2]["sentId"], 0)
        self.assertEqual(d["meta"].iloc[2]["wordId"], 2)
        self.assertEqual(d["meta"].iloc[6]["token"], "Also")
        self.assertEqual(d["meta"].iloc[6]["sentId"], 1)
        self.assertEqual(d["meta"].iloc[6]["wordId"], 0)
        self.assertEqual(d["meta"].iloc[8]["token"], "is")
        self.assertEqual(d["meta"].iloc[8]["sentId"], 1)
        self.assertEqual(d["meta"].iloc[8]["wordId"], 2)
    
    def test_classification_empty(self):
        t1 = "This is definitely a sentence."
        p = Preprocessor({})
        c, d = p.classify(t1)
        self.assertEqual(c, "wikipedia")
        self.assertEqual(d, {})

    def test_classification_basic(self):
        t1 = "This is definitely a sentence."
        p = Preprocessor({"t": set(["This"])})
        c, d = p.classify(t1)
        self.assertEqual(c, "schedules")
        self.assertEqual(d, {"t": ["This"]})
    
    def test_classification_schedules(self):
        with open("../data/keywords.json") as json_file:
            schd = json.load(json_file)
        p = Preprocessor(schd)

        def t(q, expected):
            d = p.preprocessAndClassifyQuery(q)
            self.assertEqual(d["classification"], expected)
        
        s = "schedules"
        w = "wikipedia"
        t("What quarter does Foaad teach CSC-482?", s)
        t("Who's the president of cal poly?", w)
        t("What classes is professor khosmood teaching this quarter?", s)
        t("What CSC classes are being offered next quarter?", s)

        # check dept ME vs person me issue
        t("what is me to this", w)
        t("what is ME to this", s)

    def test_findReg(self):
        p = Preprocessor({})

        c, d = p.classify("CSC 482 section 2")
        self.assertEqual(c, "schedules")
        self.assertEqual(len(d["course_numbers"]), 1)
        self.assertEqual(len(d["section_numbers"]), 1)
        self.assertEqual("482", d["course_numbers"][0])
        self.assertEqual("02", d["section_numbers"][0])

        c, d = p.classify("CSC 482 section 42")
        self.assertEqual(len(d["section_numbers"]), 1)
        self.assertEqual("42", d["section_numbers"][0])

    def test_both(self):
        t1 = "This is definitely a sentence."
        p = Preprocessor({})
        d = p.preprocessAndClassifyQuery(t1)

        self.assertEqual(d["strQuery"], t1)
        self.assertEqual(d["tokQuery"], ["This", "is", "definitely", "a", "sentence", "."])
        self.assertEqual(d["classification"], "wikipedia")
        self.assertEqual(d["cats"], {})
        self.assertEqual(d["meta"].iloc[0]["token"], "This")