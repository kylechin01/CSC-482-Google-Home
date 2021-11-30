import nltk
# nltk.download('punkt')
import re
import requests
import numpy as np
import pandas as pd
import pickle
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

def cleanText(text):
    return re.sub("(\[ edit \])|(\[[0-9]*\])", "", text)

def buildDataFrame(soup):
    bodyContent = soup.find("div", {"id": "bodyContent"})
    allText = bodyContent.find_all(["h2", "h3", "p", "tr", "li"])
    h2 = []
    h3 = []
    tags = []
    text = []
    currH2 = ""
    currH3 = ""
    for i in allText:
        tagName = i.name
        newText = cleanText(i.get_text(separator=' ')).strip()
        if tagName == "h2":
            currH2 = newText
            currH3 = ""
        elif tagName == "h3":
            currH3 = newText
        if currH2 not in ["Contents", "References", "External links", "See also"] and newText!=currH2 and newText!=currH3:
            text.append(newText)
            tags.append(tagName)
            h2.append(currH2)
            h3.append(currH3)
    df = pd.DataFrame(data={'h2':h2, 'h3':h3, 'tag':tags, 'text':text})
    df['tokenized_sents'] = df.apply(lambda row: sent_tokenize(row['text']), axis=1)
    df = df.explode('tokenized_sents').dropna().reset_index(drop=True)
    return df

def webscrapeWikipedia():
    response = requests.get("https://en.wikipedia.org/wiki/California_Polytechnic_State_University,_San_Luis_Obispo")
    soup = BeautifulSoup(response.content, "html.parser")
    df = buildDataFrame(soup)

    # Save df to file
    filename = "wikiCPSents"
    file = open(filename,'wb')
    pickle.dump(df, file)
    file.close()


def getResponse(question):
    THRESHOLD = 0.03

    # Get df from file
    filename = "wikiCPSents"
    file = open(filename,'rb')
    df = pickle.load(file)
    file.close()

    sents = df.loc[:, 'tokenized_sents']

    # Build TFIDF Vectorizer
    vec = TfidfVectorizer(norm=None, max_df=0.2)
    vec.fit(sents)
    tf_idf_sparse_sents = vec.transform(sents)

    ques = pd.Series([question])
    tf_idf_sparse_ques = vec.transform(ques)

    # Calculate cosine similarity
    a = tf_idf_sparse_ques
    B = tf_idf_sparse_sents
    dot = a.multiply(B).sum(axis=1)
    a_len = np.sqrt(a.multiply(a).sum())
    b_len = np.sqrt(B.multiply(B).sum(axis=1))
    cosSimilarity = dot / (a_len * b_len)
    cos_similarities = pd.DataFrame(cosSimilarity)[0]
    most_similar = cos_similarities.sort_values(ascending=False)

    # Get most similar sentence and its cosine similarity
    sub_df = df.loc[most_similar.head(1).index]
    sim_value = most_similar.head(1).values[0]
    ans = sub_df.iloc[0]['tokenized_sents']

    # Printing for development purposes...
    print(most_similar.head(5))
    print()
    print(df.loc[most_similar.head(5).index, 'tokenized_sents'])
    print()
    print(ans)
    print(sim_value)
    print()

    # Check if cosine similarity is below the threshold
    if sim_value < THRESHOLD:
        ans = "The answer could not be found on the Wikipedia page for Cal Poly."
    return ans

# webscrapeWikipedia()
# ans = getResponse("What is the average GPA?")
# print(ans)