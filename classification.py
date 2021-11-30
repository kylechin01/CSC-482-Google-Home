# Handles preprocessing of input and classifies it into a type of question (schedules, wikipedia, or youtube)

import pandas as pd
import spacy
import re

class Preprocessor:

    def __init__(self, schWords):
        """
        Handles preprocessing and classification. schWords should be a dictionary with each class
        corresponding to a set of relevant words or regular expression search strings.
        For example:
            {
                "instructor": {"Foaad", "Khosmood", "Franz", "Kurfess"},
                "time": {"spring", "winter", "fall", "next", "last"},
                "department": {"CSC", "college of engineering", "computer science"},
                "course": {"natural language processing", r"[0-9][0-9][0-9]"}
            }
        When a string is processed, the resultant dictionary will include which of these categories
        were found if it is classified as schedules, or an empty string for wikipedia.
        """
        self.nlp = spacy.load("en_core_web_sm")
        self.schWords = schWords
        # TODO: include the schedules word lists here

    def handleInput(self, input):
        d = self.preprocess(input)
        clasification, categories = self.classify(input)
        d["classification"] = clasification
        d["cats"] = categories

        return d

    def preprocess(self, input):
        """
        Given a string (TODO: I assume its a string) of text, preprocess it
        Returns a dictionary with attributes:
            - strQuery: original query as a string
            - tokQuery: tokenized query by word in a 1D tuple
            - meta: a pandas dataframe with the attributes described in Preprocessor.getMeta()
        """
        # tokenize the string and get metadata for each token
        doc = self.nlp(input)
        metadf = self.getMeta(doc)

        tokQuery = [tok.text for tok in doc]
        docDict = {"strQuery": input, "tokQuery": tokQuery, "meta": metadf}
        return docDict

    def getMeta(self, doc):
        """
        Given a doc denerated by spacy, organize into a dataframe with attributes:
            - sentId: starting from 0, the index of the sentence
            - wordId: starting from 0, the index of the token in the sentence
            - token:  the actual token as a string
            - pos:    part of speech
            - lemma:  lemma version of the stopword
            - alpha:  True if the token is only alphabetic letters
            - stop:   True for stopword else False
        """
        cols = ["sentId", "wordId", "token", "pos", "lemma", "alpha", "stop"]
        df = pd.DataFrame(columns=cols)

        sc = -1
        wc = 0
        i = 0
        for token in doc:
            # add a new row to the dataframe for each token
            if token.is_sent_start:
                sc += 1
                wc = 0
            df.loc[i] = [sc, wc, token.text, token.pos_, token.lemma_, token.is_alpha, token.is_stop]
            wc += 1
            i += 1
        return df
    
    def classify(self, query):
        """
        Given a query, return its classification
        Classifications include:
            "schedules" : can be answered from information on the cal poly schedules page
            "wikipedia" : answer will be from cal poly wikipedia
            "youtube"   : answer requires a lookup through the youtube api # TODO: ask foaad if we should keep this cal poly related, or allow any songs to be played
        Returns a tuple of a string and a list of discovered categories for schedules
        """
        # TODO
        discovered = []
        for cat in self.schWords:
            for pat in self.schWords[cat]:
                if re.search(pat, query):
                    discovered.append(cat)
                    break
        return (("schedules" if len(discovered) > 0 else "wikipedia"), tuple(discovered),)