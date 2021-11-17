import re
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup



response = requests.get("https://en.wikipedia.org/wiki/California_Polytechnic_State_University,_San_Luis_Obispo")
soup = BeautifulSoup(response.content, "html.parser")

h2Headers = soup.find_all(["h2", "h3", "p"])
print(len(h2Headers))
for i in range(13):
    print(h2Headers[i].get_text())
    print()

def clean_text(text):
    re.sub("(\[edit\])|(\[0-9\])", "", text)
    return text
        