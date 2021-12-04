from typing import AnyStr
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
    allText = bodyContent.find_all(["h2", "h3", "p", "li"])
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
    tablesDF = pd.read_html(response.content)

    df = buildDataFrame(soup)

    # Order of list of tables:
    #   1. Basic Info (Motto/President/etc)
    #   2. Academic Stats (Applicants/Enrolled/GPA/SAT/etc) TODO
    #   3. Rankings
    #   4. Demographics TODO
    #   5. Rivals
    #   6. Sentences
    allDF = []
    
    tablesDF[0] = tablesDF[0].rename(columns={0:"A", 1:"B"})
    tablesDF[0]["A"] = tablesDF[0]["A"].str.replace("\[[0-9]*\]", "", regex=True).str.strip()
    tablesDF[0]["B"] = tablesDF[0]["B"].str.replace("\[[0-9]*\]", "", regex=True).str.strip()
    tablesDF[0] = tablesDF[0].dropna()
    tablesDF[0] = tablesDF[0].loc[tablesDF[0]["A"]!="Colors"]
    allDF.append(tablesDF[0])
    
    tablesDF[1] = tablesDF[1].dropna().rename(columns={tablesDF[1].columns[0]:"Category"})
    allDF.append(tablesDF[1])

    tablesDF[2][tablesDF[2].columns[0]] = tablesDF[2][tablesDF[2].columns[0]].str.replace("\[[0-9]*\]", "", regex=True).str.strip()
    tablesDF[2] = tablesDF[2].loc[tablesDF[2][tablesDF[2].columns[0]]!=tablesDF[2][tablesDF[2].columns[1]]]
    allDF.append(tablesDF[2])

    tablesDF[4] = tablesDF[4].rename(columns=lambda x: re.sub('\[[0-9]*\]','',x.strip())).rename(columns={tablesDF[4].columns[0]:"Demographic"})
    allDF.append(tablesDF[4])

    tablesDF[7] = tablesDF[7].rename(columns={0:"A", 1:"B"})
    allDF.append(tablesDF[7])
    allDF.append(df)

    # Save allDF to file
    filename = "wikiCPSents"
    file = open(filename,'wb')
    pickle.dump(allDF, file)
    file.close()

def getDF():
    # Get df from file
    filename = "wikiCPSents"
    file = open(filename,'rb')
    allDF = pickle.load(file)
    file.close()

    sents = allDF[5].loc[:, 'tokenized_sents']

    # Build TFIDF Vectorizer
    vec = TfidfVectorizer(norm=None, max_df=0.2)
    vec.fit(sents)
    tf_idf_sparse_sents = vec.transform(sents)

    return (allDF, vec, tf_idf_sparse_sents)

def getResponseSents(df, vec, tf_idf_sparse_sents, question):
    THRESHOLD = 0.2

    ques = pd.Series([question])
    tf_idf_sparse_ques = vec.transform(ques)

    # Calculate cosine similarity
    a = tf_idf_sparse_ques
    B = tf_idf_sparse_sents
    dot = a.multiply(B).sum(axis=1)
    a_len = np.sqrt(a.multiply(a).sum())
    b_len = np.sqrt(B.multiply(B).sum(axis=1))
    # print(a_len * b_len)
    cosSimilarity = dot / (a_len * b_len)
    cos_similarities = pd.DataFrame(cosSimilarity)[0]
    most_similar = cos_similarities.sort_values(ascending=False)

    # Get most similar sentence and its cosine similarity
    sub_df = df.loc[most_similar.head(1).index]
    sim_value = most_similar.head(1).values[0]
    ans = sub_df.iloc[0]['tokenized_sents']

    # Printing for development purposes...
    # print(most_similar.head(5))
    # print()
    # print(df.loc[most_similar.head(5).index, 'tokenized_sents'])
    # print()
    # print(ans)
    # print(sim_value)
    # print()

    # Check if cosine similarity is below the threshold
    if sim_value < THRESHOLD:
        print(ans)
        ans = "The answer could not be found on the Wikipedia page for Cal Poly."
    return ans

def getResponse(allDF, vec, tf_idf_sparse_sents, question):
    ans = ""
    if("ranking" in question.lower()):
        cnt = 0
        for ind, row in allDF[2].iterrows():
            ans += row[allDF[2].columns[0]] + " ranks Cal Poly as " + row[allDF[2].columns[1]] + ". "
            cnt += 1
            if(cnt>=3):
                return ans
    else:
        for ind, row in allDF[4].iterrows():
            s = row["A"].lower()
            if s.endswith("s"):
                s = s[:len(s)-1]
            if s in question.lower():
                ans = allDF[4].loc[ind, "A"] + " are " + allDF[4].loc[ind, "B"] + "."
                return ans
    
        for ind, row in allDF[0].iterrows():
            s = row["A"].lower()
            if s in question.lower():
                ans = allDF[0].loc[ind, "B"] + "."
                return ans

        ans = getResponseSents(allDF[5], vec, tf_idf_sparse_sents, question)
        return ans

# webscrapeWikipedia()
# ans = getResponse("What is the average GPA?")
# print(ans)