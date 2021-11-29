import re
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup, SoupStrainer

base_url = "http://schedules.calpoly.edu/"

# Given a container, return true iff the container has the specified attribute 
# and the attributes value matches the given pattern.
def attr_contains(cont, attr, pattern):
	if not cont.has_attr(attr):
		return False
	attr_vals = cont[attr]
	for val in attr_vals:
		if re.match(pattern, val):
			return True
	return False

# Given a page url, returns the pair of links that lead to the previous and future
# term versions of that page.
def get_temporal_links(url):
	response = requests.get(url)
	link_strainer = SoupStrainer("a")	
	link_soup = BeautifulSoup(
		response.content, 
		"html.parser", 
		parse_only=link_strainer
	)
	output = []
	for a in link_soup:
		spans = a.find_all("span")
		for span in spans:
			if attr_contains(span, "class", "(.+prev)|(.+next)"):
				output.append(base_url + a["href"])
	return output

foo = get_temporal_links("https://schedules.calpoly.edu/classes_CSC-225_last.htm")
print(foo)