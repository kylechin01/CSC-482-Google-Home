# Tests functions in classification.py including preprocessing

import unittest
import sys
sys.path.append('../')

from classification import *

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
        # TODO more throughoughough testing?
    
    def test_classification_empty(self):
        t1 = "This is definitely a sentence."
        p = Preprocessor({})
        c, d = p.classify(t1)
        self.assertEqual(c, "wikipedia")
        self.assertEqual(d, tuple([]))

    def test_classification_basic(self):
        t1 = "This is definitely a sentence."
        p = Preprocessor({"t": set(["This"])})
        c, d = p.classify(t1)
        self.assertEqual(c, "schedules")
        self.assertEqual(d, tuple(["t"]))
    
    def test_classification_schedules(self):
        schd = {
            "instructor": {"Foaad", "Khosmood", "Franz", "Kurfess"},
            "time": {"spring", "winter", "fall", "summer", "next", "last"},
            "department": {"CSC", "college of engineering", "computer science"},
            "course": {"natural language processing", r"[0-9][0-9][0-9]"}
        }
        p = Preprocessor(schd)

        def t(q, expected):
            d = p.preprocessAndClassifyQuery(q)
            self.assertEqual(d["classification"], expected)
        
        s = "schedules"
        w = "wikipedia"
        t("What quarter does Foaad teach CSC-482?", s)
        t("Who's the president of cal poly?", w)
        # TODO: more intense testing

    def test_both(self):
        t1 = "This is definitely a sentence."
        p = Preprocessor({})
        d = p.preprocessAndClassifyQuery(t1)

        self.assertEqual(d["strQuery"], t1)
        self.assertEqual(d["tokQuery"], ["This", "is", "definitely", "a", "sentence", "."])
        self.assertEqual(d["classification"], "wikipedia")
        self.assertEqual(d["cats"], tuple([]))
        self.assertEqual(d["meta"].iloc[0]["token"], "This")