import pandas as pd
import re
import json

class Processor:
    def __init__(self, dfs):
        # The schedules dataframes, stored as a dict with the key being the
        # dataframe name and the value being the dataframe itself
        self.dfs = dfs
        # A list of all the dataframe names
        self.table_names = dfs.keys()
        # A dict that contains words used to identify what dataframe to use
        # in order to answer the query.
        self.df_identifiers = {key: [] for key in self.table_names}
        self.df_identifiers["classes"] = [
            "class",
            "section",
            "lecture",
            "lab",
            "days",
            "start",
            "end",
            "teaches"
            "professor"
            "instructor"
            "teacher",
            "enroll",
            "waitlist",
            "drop",
            "[A-Z][A-Z][A-Z]?[A-Z]?"
        ]
        # for name in self.table_names:
        #     self.df_identifiers[name] = list(self.dfs[name].columns.values)

    # Given a query, respond with an appropriate answer.
    def getResponse(self, qp):
        query_lemmas = qp["meta"]["lemma"].tolist()
        query_keywords = qp["cats"]

        print("Schedules query received: " + qp["strQuery"])
        print("Lemmatized toks from query: " + str(query_lemmas))
        print("Keywords from query: \n" + json.dumps(query_keywords, 
            sort_keys=True, indent=4))

        num_hits = {key: 0 for key in self.table_names}
        for lemma in query_lemmas:
            for df_name, df_identifier in self.df_identifiers.items():
                for identifier in df_identifier:
                    if re.match(identifier, lemma):
                        print("Identifier hit found on \"" + lemma + "\" for " + df_name)
                        num_hits[df_name] += 1
        print(num_hits)
        return

    def determineColumnMeaning():
        return


    # Determine the kind of questions we can answer.
    def determineQuestionType(self, lemmas, keywords):
        if "office" in lemmas:
            # The query is about office hours or office location.
            return self.handleOfficeQuestion(keywords)
        elif "section_number" in keywords:
            return self.handleClassQuestion(keywords)
        elif ("name" in lemmas or "description" in lemmas) and \
            "course_number" in keywords:
            return self.handleNameOfCourseQuestion(keywords)
        # TODO, google may parse GE as two words
        elif ("general" in lemmas or "GE" in lemmas) and \
            "course_number" in keywords:
            return self.handleGEsOfCourseQuestion(keywords)
        # TODO fix prereq for google parsings
        elif ("requirements" in lemmas or "prereq" in lemmas) and \
            "course_number" in keywords:
            return self.handleRequirementsOfCourseQuestion(keywords)
        elif ("name" in lemmas or "description" in lemmas) and \
            "course_number" in keywords:
            return self.handleNameOfClassQuestion(keywords)
        elif ("start" in lemmas or "end" in lemmas or "days" in lemmas) and \
            len(keywords["department_codes"]) > 0 and len(keywords["classes"]) > 0:
            return self.handleClassQuestion(keywords)
        elif len(keywords["instructor_names"]) > 0:
            # Only professor name was given, return information about that
            # professor. 
            return self.handleInstructorQuestion(keywords)
        else:
            return "I\'m sorry, I don't understand the question."

    """
    Returns the relevant row (or rows) of the Instructors table
    according to the input. If multiple rows are to be returned,
    additionally state the number of rows that were returned and
    read all results out up to a limit of 3 rows.   
    """
    def handleOfficeQuestion(self, keywords):
        name = keywords["instructor_names"]
        return ""

    # TODO
    def handleInstructorQuestion(self, keywords):
        return ""

    # TODO
    def handleClassQuestion(self, keywords):
        df_classes = self.dfs["classses"]
        # res = df_classes.loc["Name" == keywords["course_numbers"]
        #     "Section" == keywords["section_numbers"]
        return None

    # TODO
    def handleNameOfCourseQuestion(self, keywords):
        return ""

    # TODO
    def handleGEsOfCourseQuestion(self, keywords):
        return ""

    # TODO
    def handleRequirementsOfCourseQuestion(self, keywords):
        return ""

    # TODO
    def handleNameOfClassQuestion(self, keywords):
        return ""

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
# Is Professor Seng teaching next quarter?
# What classes is Professor Foaad teaching next quarter?
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
