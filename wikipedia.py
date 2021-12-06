import nltk
import spacy
# nltk.download('punkt')
import re
import requests
import numpy as np
import pandas as pd
import pickle
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords

def cleanText(text):
    return re.sub("(\[.*\])|(\[[0-9]*\])", "", text)

def lemmatizeSent(s, nlp):
    doc = nlp(s)
    ret = []
    for token in doc:
      ret.append(token.lemma_)
    return " ".join(ret)

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
    nlp = spacy.load("en_core_web_sm")
    df['lemmatize_sent'] = df['tokenized_sents'].apply(lemmatizeSent, args=(nlp,))
    return df

def webscrapeWikipedia():
    response = requests.get("https://en.wikipedia.org/wiki/California_Polytechnic_State_University,_San_Luis_Obispo")
    soup = BeautifulSoup(response.content, "html.parser")
    tablesDF = pd.read_html(response.content)

    df = buildDataFrame(soup)

    # Order of list of tables:
    #   0. Basic Info (Motto/President/etc)
    #   1. Rankings
    #   2. Demographics
    #   3. Rivals
    #   4. Sentences
    #   5. Academics
    allDF = []
    
    tablesDF[0] = tablesDF[0].rename(columns={0:"A", 1:"B"})
    tablesDF[0]["A"] = tablesDF[0]["A"].str.replace("\[[0-9]*\]", "", regex=True).str.strip()
    tablesDF[0]["B"] = tablesDF[0]["B"].str.replace("\[[0-9]*\]", "", regex=True).str.strip()
    tablesDF[0] = tablesDF[0].dropna()
    tablesDF[0] = tablesDF[0].loc[tablesDF[0]["A"]!="Colors"]
    allDF.append(tablesDF[0])

    tablesDF[2][tablesDF[2].columns[0]] = tablesDF[2][tablesDF[2].columns[0]].str.replace("\[[0-9]*\]", "", regex=True).str.strip()
    tablesDF[2] = tablesDF[2].loc[tablesDF[2][tablesDF[2].columns[0]]!=tablesDF[2][tablesDF[2].columns[1]]]
    allDF.append(tablesDF[2])

    tablesDF[4] = tablesDF[4].rename(columns=lambda x: re.sub('\[[0-9]*\]','',x.strip()))
    allDF.append(tablesDF[4])

    tablesDF[7] = tablesDF[7].rename(columns={0:"A", 1:"B"})
    allDF.append(tablesDF[7])
    allDF.append(df)

    tablesDF[1] = tablesDF[1].dropna().rename(columns={tablesDF[1].columns[0]:"Category"}).drop(1).reset_index(drop=True)
    tablesDF[1].at[1, 'Category'] = 'Admit'
    tablesDF[1].at[4, 'Category'] = 'ACT'
    tablesDF[1].at[5, 'Category'] = 'SAT'
    allDF.append(tablesDF[1])

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

    # sents = allDF[4].loc[:, 'tokenized_sents']
    sents = allDF[4].loc[:, 'lemmatize_sent']

    # Build TFIDF Vectorizer
    vec = TfidfVectorizer(norm=None, max_df=0.2, stop_words=stopwords.words('english'))
    vec.fit(sents)
    tf_idf_sparse_sents = vec.transform(sents)

    return (allDF, vec, tf_idf_sparse_sents)

def getResponseSents(df, vec, tf_idf_sparse_sents, question):
    THRESHOLD = 0.3

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
    sim_value = most_similar.head(1).values[0]
    print(sim_value)
    # Check if cosine similarity is below the threshold
    if pd.isna(sim_value) or sim_value < THRESHOLD:
        return ""

    ind = most_similar.head(1).index
    sub_df = df.loc[ind]
    ans = ""
    if ind>0:
        sub_df_other = df.loc[ind-1]
        if(sub_df_other.iloc[0]['h3']==sub_df.iloc[0]['h3'] and sub_df_other.iloc[0]['tag']==sub_df.iloc[0]['tag']):
            ans += sub_df_other.iloc[0]['tokenized_sents'] + ". "
    ans += sub_df.iloc[0]['tokenized_sents'] + ". "
    if ind<len(df)-1:
        sub_df_other = df.loc[ind+1]
        if(sub_df_other.iloc[0]['h3']==sub_df.iloc[0]['h3'] and sub_df_other.iloc[0]['tag']==sub_df.iloc[0]['tag']):
            ans += sub_df_other.iloc[0]['tokenized_sents'] + ". "

    # Printing for development purposes...
    # print(most_similar.head(5))
    # print()
    # # print(df.loc[most_similar.head(5).index, 'tokenized_sents'])
    # print(df.loc[most_similar.head(5).index, 'lemmatize_sent'])
    # print()
    # print(ans)
    # print()

    return ans

def getLemmatizedQues(qd):
    x = qd['meta'].loc[qd['meta']['stop']==False, 'lemma'].values
    x = " ".join(x)
    # return qd['strQuery']
    return x

def getResponse(allDF, vec, tf_idf_sparse_sents, quesDict):
    question = getLemmatizedQues(quesDict).lower()
    nlp = spacy.load("en_core_web_sm")

    ans = ""
    if(" rank" in question.lower()):
        cnt = 0
        for ind, row in allDF[1].iterrows():
            ans += row[allDF[1].columns[0]] + " ranks Cal Poly as " + row[allDF[1].columns[1]] + ". "
            cnt += 1
            if(cnt>=3):
                return ans
    else:
        for ind, row in allDF[3].iterrows():
            s = lemmatizeSent(row["A"], nlp).lower()
            if s in question:
                ans = allDF[3].loc[ind, "A"] + " are " + allDF[3].loc[ind, "B"] + "."
                return ans
    
        for ind, row in allDF[0].iterrows():
            s = lemmatizeSent(row["A"], nlp).lower()
            flag = "student" in s and "how many" not in quesDict['strQuery'].lower()
            if s in question:
                if flag:
                    continue
                ans = allDF[0].loc[ind, "B"] + "."
                return ans

        for ind, row in allDF[5].iterrows():
            s = " " + lemmatizeSent(row["Category"], nlp).lower() + " "
            if s in question:
                ans = allDF[5].loc[ind, "Category"]
                if(row['Category']=='Admit'):
                    ans += " %"
                ans += " is " + str(allDF[5].loc[ind, allDF[5].columns[1]])
                return ans

        if("percent" in question):
            for ind, row in allDF[2].iterrows():
                s = lemmatizeSent(row[allDF[2].columns[0]], nlp).lower()
                s = re.split('/| ',s)
                s = [w for w in s if w]
                for x in s:
                    if x=="male" and x not in question.replace("female", ""):
                        continue
                    if x in question and "american" not in x:
                        perc = allDF[2].loc[ind, allDF[2].columns[1]]
                        if(perc=="Null"):
                            perc = "none"
                        ans = allDF[2].loc[ind, allDF[2].columns[0]] + " make up " + perc + " of Cal Poly."
                        return ans

        ans = getResponseSents(allDF[4], vec, tf_idf_sparse_sents, question)
        return ans.replace("\"", "")

# webscrapeWikipedia()
# ans = getResponse("What is the average GPA?")
# print(ans)