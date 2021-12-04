import pandas as pd
import re

class Processor:
    def __init__(self, dfs):
        self.dfs = dfs

    def process_query(query, found_keywords):
        return

    def access_database(table, loc_id):
        return


class Query:
    # A query will ask for one of the following:
    def __init__(self, dfs):
        return

# Query assumptions:
#   Term is current

# === Answer is just a cell in the db ===
# What time does CSC 482 section 02 start?
#   course keyword: [CSC, 482]
#   class keyword: [02]
#   question keyword: [time, start]
#   => source_db = classes
# What building is CSC 482 02 be in?
# 
# When was the last time CSC 480 was offered?
# When is CPE 400 next offered?

# === Answer is a count of matching rows ===
# How many sections of CPE 101 are offered?
# How many different courses is the CS department offering?
# How many sections of CPE 315 are taught by Seng?

# === Answer is a list rows ===
# Is Professor Seng teaching this quarter?
# What classes is Professor Foaad teaching next quarter?i
# How many different professors are teaching CSC 482?
# Which professors are teaching CSC 482 this quarter?
# What departments are in the college of engineering?
# Can I take both CSC 482 and CSC 483 next quarter?
# Does ENGL 124 and MATH 143 conflict next quarter?

# === Question is not specific enough ===
# Is CPE 430 with Professor Clements full?
# How often is CSC 482 offered?
# What time is CSC 101?
# How many people are on the waitlist for CPE 123?

