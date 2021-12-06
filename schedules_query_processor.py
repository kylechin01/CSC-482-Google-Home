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
        # TODO, keywords.json should export the current term for easy extraction
        self.current_term = 2218
        # TThe term that the query is about, defaulting to the current term
        self.specified_term = self.current_term

    # Given a query, respond with an appropriate answer.
    def getResponse(self, qp):
        query_lemmas = qp["meta"]["lemma"].tolist()
        query_keywords = qp["cats"]

        print("Schedules query received: " + qp["strQuery"])
        print("Lemmatized toks from query: " + str(query_lemmas))
        print("Keywords from query: \n" + json.dumps(query_keywords, 
            sort_keys=True, indent=4))

        return self.determineQuestionType(query_lemmas, query_keywords)

    """
    Given the list of query lemmas, query keywords, and target lemmas, return true 
    if at least one of the query lemmas is in the list of target lemmas. If a list
    of target keyword catergories is supplied, then return true when at least one 
    of the query lemmas is in the list of target lemmas and all elements of the
    target keyword categories is in query keywords. Return false otherwise.
    """ 
    def filterQuestion(self, query_lemmas, keywords, target_lemmas, target_cats = []):
        at_least_one_lemma_found = False
        if len(target_lemmas) == 0:
            at_least_one_lemma_found = True
            # a tad inefficient here 
        for q_lemma in query_lemmas:
            for t_lemma in target_lemmas:
                if t_lemma in q_lemma:
                    at_least_one_lemma_found = True
        if len(target_cats) == 0:
            return at_least_one_lemma_found
        at_least_one_keyword_cat_missing = False
        for target_cat in target_cats:
            if target_cat not in keywords or len(keywords[target_cat]) == 0:
                at_least_one_keyword_cat_missing = True
        return at_least_one_lemma_found and not at_least_one_keyword_cat_missing
                
    """
    Collapse various lemmas into a standardized version.
    """
    def normalizeLemma(self, lemma):
        lemma = lemma.lower()
        if lemma in ["teacher", "professor", "prof", "instructor", "lecturer"]:
            return "instructor"
        elif lemma in ["begin"]:
            return "start"
        elif lemma in ["class"]:
            return "course"
        elif lemma in ["place, building"]:
            return "location"
        elif lemma in ["quarter"]:
            return "term"
        elif lemma in ["spring"]:
            return "Spring"
        elif lemma in ["winter"]:
            return "Summer"
        elif lemma in ["autumn", "fall"]:
            return "Fall"
        elif lemma in ["winter"]:
            return "Winter"
        return lemma

    """
    Get the term that the user is specifiying in their query. If no specification is made,
    default to the current term. Return None when a term is specified with incomplete information
    (ex. no year is given) or does not exist (ex. Spring 2050).
    """
    def getTerm(self, lemmas, keywords):
        if self.filterQuestion(lemmas, keywords, ["term", "Spring", "Summer", "Fall", "Winter"]):
            if self.filterQuestion(lemmas, keywords, ["this"]):
                return self.current_term
            elif self.filterQuestion(lemmas, keywords, ["next"]):
                if self.current_term % 10 == 8:
                    return self.current_term + 4
                return self.current_term + 2
            elif self.filterQuestion(lemmas, keywords, ["previous", "last"]):
                if self.current_term % 10 == 2:
                    return self.current_term - 4
                return self.current_term - 2
            elif self.filterQuestion(lemmas, keywords, ["Spring", "Summer", "Fall", "Winter"]):
                query_year = None
                query_season = None
                for lemma in lemmas:
                    if re.match("[0-9][0-9][0-9][0-9]", lemma):
                        query_year = lemma
                    elif re.match("([sS]pring)|([sS]ummer)|([fF]all)|([wW]inter)", lemma):
                        query_season = lemma
                if query_year and query_season:
                    return self.getTermIdFromKeywords(query_year, query_season)
                return None
            return
        return self.current_term

    """
    Determines the intent of the query and attempts to answer said intent.
    """
    def determineQuestionType(self, lemmas, keywords):
        lemmas = [self.normalizeLemma(le) for le in lemmas]

        term = self.getTerm(lemmas, keywords)
        if term:
            self.specified_term = term
        else:
            return "I could not find any term that matches those values."
        term_string = ""
        if self.specified_term != self.current_term:
            term_string = f"For {self.getTermNameFromId(self.specified_term).iloc[0]}, "

        if self.filterQuestion(lemmas, keywords, ["when", "time"], 
            ["department_codes", "course_numbers", "section_numbers"]):
            """
            The question is asking about class times and provides a pseudo-primary
            key for the classes table (-ish, the given keywords due not constitute 
            the entirety of the class table's primary key).
            """
            return term_string + self.handleClassTimeQuestion(keywords)
        elif self.filterQuestion(lemmas, keywords, ["teach"], ["instructor_names"]):            
            # The question is asking about which classes the given professor teaches
            return term_string + self.handleClassProfessorQuestion(keywords)
        elif self.filterQuestion(lemmas, keywords, ["enrol", "capacity", "waitlist", "drop"],
            ["department_codes", "course_numbers", "section_numbers"]):
            # The question is asking the enrollments of a class
            return term_string + self.handleClassEnrollmentsQuestion(keywords)
        elif self.filterQuestion(lemmas, keywords, ["who", "where", "instructor", "building"],
            ["department_codes", "course_numbers", "section_numbers"]):
            # The question is asking the location or professor of a class
            return term_string + self.handleClassDetailsQuestion(keywords)
        elif "office" in lemmas:
            # The query is about office hours or office location.
            return term_string + self.handleOfficeQuestion(keywords)
        elif self.filterQuestion(lemmas, keywords,\
        ["name", "description", "general", "GE", "ge", "gen", "ed"], ["course_numbers"]):
            # The query is about a course name or ge
            return term_string + self.handleCourseQuestion(keywords)
        elif self.filterQuestion(lemmas, keywords, ["GE", "ge"]) and re.match(".*[A-Za-z][0-9].*", " ".join(lemmas)):
            # The query is about finding satisfying classes for a GE
            GE = re.search("([A-Za-z][0-9])", " ".join(lemmas))[1]
            return term_string + self.handleCourseByGEQuestion(keywords, GE)
        elif self.filterQuestion(lemmas, keywords, ["course", "offer", "teach"], ["department_codes"]):
            return term_string + self.handleCourseByDepartmentQuestion(keywords)
        else:
            # Returning an empty string indicates the answer may be in wikipedia
            return ""

    """
    Returns the relevant row (or rows) of the Instructors table
    according to the input. If multiple rows are to be returned,
    additionally state the number of rows that were returned and
    read all results out up to a limit of 3 rows.   
    """
    def handleOfficeQuestion(self, keywords):
        # Get the row for the correct professor
        resDf = self.dfs["instructors"]
        resDf = resDf[resDf["Term"] == self.specified_term]
        name = self.getProfessorNameFromKeywords(resDf, keywords["instructor_names"])
        resDf = resDf[resDf["Name"] == name]

        if len(resDf) <= 0:
            return "Sorry, I cannot find information on that instructor"

        # format response return
        res = resDf.iloc[0]
        profName = res['Name'].split(',')[0]
        ohLoc = [r.lstrip("0") for r in res["Office Location"].split("-")]
        dept = res["Department"]
        return f"Professor {profName} from department {dept} has office hours in building {ohLoc[0]} room {ohLoc[1]}"

    def handleCourseByDepartmentQuestion(self, keywords):
        df = self.dfs["courses"]
        # Assuming only one specified department
        department = keywords["department_codes"][0]

        course_number = None
        if "course_numbers" in keywords:
            course_number = keywords["course_numbers"][0]

        if course_number:
            df_res = df.loc[(df["Department"] == department) &
                (df["Id"].str.contains(course_number)) &
                (df["Term"] == self.specified_term)]
            if df_res.empty:
                return f"{department} {course_number} is not offered."

            df_classes = self.dfs["classes"]
            section_count_df = df_classes.loc[(df_classes["Name"].str.contains(department)) &
                (df_classes["Name"].str.contains(course_number)) &
                (df_classes["Term"] == self.specified_term)]
            section_count = section_count_df.shape[0]
            return f"{department} {course_number} is offered. There are {section_count} sections of the course. "

        df_res = df.loc[(df["Department"] == department) &
                (df["Term"] == self.specified_term)]
        
        if df_res.empty:
            return f"The {department} is not offering any courses."

        num_rows = df_res.shape[0]
        output = f"There are {num_rows} {department} courses being offered: "
        i = 0
        while i < 3 and i < num_rows:
            output += df_res.iloc[i]["Id"] + ", "
            i += 1
        if i < num_rows:
            output += f"and {num_rows - i} others"
        return output + "."

    def handleCourseQuestion(self, keywords):
        """
        Given a number of a course, return the course description
        """
        dept = keywords["department_codes"][0]
        courseNum = keywords["course_numbers"][0]
        courseid = f"{dept} {courseNum}"

        coursesDf = self.dfs["courses"]
        coursesDf = coursesDf[coursesDf["Id"] == courseid]
        coursesDf = coursesDf[coursesDf["Term"] == coursesDf["Term"].max()]

        courseDesc = coursesDf.iloc[0]["Description"]
        geStr = coursesDf.iloc[0]["GE"]
        ges = []
        if isinstance(geStr, str):
            for i in range(0, len(geStr), 2):
                x = geStr[i:i+2]
                if x != "GE":
                    ges.append(x)
        
        return f"{courseid} is called {courseDesc}" + ("" if len(ges) < 1\
            else " and it satisfies the following general education requirements " + " ".join(ges))

    def handleClassDetailsQuestion(self, keywords):
        df = self.dfs["classes"]
        class_name = list(map(lambda i, j : i + " " + j, 
            keywords["department_codes"], keywords["course_numbers"]))[0]
        section_number = int(keywords["section_numbers"][0])
        df_res = df.loc[(df["Name"] == class_name) & 
            (df["Section"] == section_number) &
            (df["Term"] == self.specified_term)]
        if df_res.empty:
            output = "I could not find any classes that match that description."
        else:
            location_toks = df_res['Location'].iloc[0].split("-")
            building_no = location_toks[0]
            room_no = location_toks[1]
            output = f"{df_res['Name'].iloc[0]} section {df_res['Section'].iloc[0]} is a {df_res['Type'].iloc[0]} class " + \
                f"taught by Professor {df_res['Instructor'].iloc[0].split(',')[0]} at building {building_no} room {room_no}."
        return output

    def handleClassEnrollmentsQuestion(self, keywords):
        df = self.dfs["classes"]
        class_name = list(map(lambda i, j : i + " " + j, 
            keywords["department_codes"], keywords["course_numbers"]))[0]
        section_number = int(keywords["section_numbers"][0])
        df_res = df.loc[(df["Name"] == class_name) & 
            (df["Section"] == section_number) &
            (df["Term"] == self.specified_term)]
        if df_res.empty:
            output = "I could not find any classes that match that description."
        else:
            output = f"{df_res['Name'].iloc[0]} section {df_res['Section'].iloc[0]} has a maximum enrollment capacity of " + \
                f"{df_res['Enrollment Capacity'].iloc[0]}. There are currently {df_res['Enrollment Count'].iloc[0]} students " + \
                f"enrolled, with {df_res['Waitlist Count'].iloc[0]} on the waitlist."
        return output

    def handleClassProfessorQuestion(self, keywords):
        df = self.dfs["classes"]
        professor_name = self.getProfessorNameFromKeywords(self.dfs["instructors"], keywords["instructor_names"])
        professor_name_trunc = re.search("^(.+, [A-Z]).*", professor_name)[1]
        df_res = df.loc[(df["Instructor"] == professor_name_trunc) & 
            (df["Term"] == self.specified_term)]
        class_names = set(df_res["Name"])
        output = f"Professor {professor_name} is teaching {len(class_names)} classes. "
        if len(class_names) > 0:
            output += "These classes are "
        for class_name in class_names:
            output += class_name + ", "
        return output

    def handleClassTimeQuestion(self, keywords):
        df = self.dfs["classes"]
        class_names = list(map(lambda i, j : i + " " + j, 
            keywords["department_codes"], keywords["course_numbers"]))
        indices = list(map(lambda i, j : [i, int(j)], 
            class_names, keywords["section_numbers"]))
        df_results = []
        for index in indices:
            df_res = df.loc[(df["Name"] == index[0]) & 
                (df["Section"] == index[1]) &
                (df["Term"] == self.specified_term)]
            if not df_res.empty:
                df_results.append(df_res)
        output = ""
        if len(df_results) == 0:
            output += "I could not find any classes that match that description."
        elif len(df_results) > 1:
            output += "A total of " + str(len(df_results)) + "results were found."
        for res in df_results:
            output += f"{res['Name'].iloc[0]} section {res['Section'].iloc[0]} is a " + \
                f"{res['Days'].iloc[0]} class that starts at {res['Start Time'].iloc[0]} " + \
                f"and ends at {res['End Time'].iloc[0]}."
        return output

    def handleCourseByGEQuestion(self, keywords, GE):
        df = self.dfs["courses"]
        if len(keywords["department_codes"]) > 0:
            department_code = keywords["department_codes"][0]
            df_res = df.loc[(df["GE"].str.contains(GE.upper())) &
                (df["Department"] == department_code) &
                (df["Term"] == self.specified_term)]
        else:
            df_res = df.loc[(df["GE"].str.contains(GE.upper())) &
                (df["Term"] == self.specified_term)]

        num_rows = df_res.shape[0]
        
        if num_rows == 0:
            output = "There are no "
        elif num_rows == 1:
            output = "There is 1 "
        else:
            output = f"There are {num_rows} "

        if len(keywords["department_codes"]) > 0:
            output += str(department_code) + " " 

        if num_rows == 1:
            output += "course "
        else:
            output += "courses "
        output += f"that satisfy the {GE} GE"
        if num_rows == 0:
            return output + "."
        
        output += ": "
        i = 0
        while i < 3 and i < num_rows:
            output += df_res.iloc[i]["Id"] + ", "
            i += 1
        if i < num_rows:
            output += f"and {num_rows - i} others"
        return output + "."

    def getTermIdFromKeywords(self, term_year, term_season):
        df = self.dfs["terms"]    
        res = df[df["Name"].str.contains(term_year) & df["Name"].str.contains(term_season)]
        if res.empty:
            return None
        return res["Id"].iloc[0]

    def getTermNameFromId(self, term_id):
        df = self.dfs["terms"]
        return df.loc[df["Id"] == term_id]["Name"]

    def getProfessorNameFromKeywords(self, df, namesList):
        """
        Given a list of names in keywords list and the dataframe to search in,
        return the actual name of the professor as expected in instructors dataframe
        """
        if len(namesList) <= 0:
            return None
        instrs = df["Name"]
        for instr in instrs:
            if isinstance(instr, str) and all([name in instr for name in namesList]):
                # all values in names list are in this instructor name
                return instr
        return None

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
