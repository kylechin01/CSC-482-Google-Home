import sys
import numpy as np
import pandas as pd
import json
import re

def extract_unique_vals(df, col):
    return df[col].unique()

# Numpy encoder code by Burhan Rashid from 
# https://stackoverflow.com/questions/57269741/typeerror-object-of-type-ndarray-is-not-json-serializable
class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32,
                              np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def clean_instructor_names(instructor_names):
    name_set = set([])
    for name in instructor_names:
        if type(name) == str:
            name = re.sub(",|\.|\+", "", name)
            toks = name.split()
            for tok in toks:
                if len(tok) > 1:
                    name_set.add(tok)
    return list(name_set)

def main():
    # Load tables
    df_classes = pd.read_csv("data/classes.csv", encoding="ISO-8859-1")
    df_courses = pd.read_csv("data/courses.csv", encoding="ISO-8859-1")
    df_departments = pd.read_csv("data/departments.csv", encoding="ISO-8859-1")
    df_instructors = pd.read_csv("data/instructors.csv", encoding="ISO-8859-1")
    df_locations = pd.read_csv("data/locations.csv")
    df_dates = pd.read_csv("data/special_dates.csv")
    df_terms = pd.read_csv("data/terms.csv")

    # Verify df indices
    df_classes.set_index(["Name", "Section", "Id", "Term"], verify_integrity=True)
    df_courses.set_index(["Id", "Type", "Term"], verify_integrity=True)
    df_departments.set_index(["Code", "Term"], verify_integrity=True)
    df_instructors.set_index(["Alias", "Department", "Term"], verify_integrity=True)
    df_locations.set_index(["Id", "Term"], verify_integrity=True)
    df_dates.set_index(["Id", "Term"], verify_integrity=True)
    df_terms.set_index("Id", verify_integrity=True)

    # Make keywords dict
    keywords = {}
    keywords["course_names"] = extract_unique_vals(df_courses, "Description")
    keywords["department_codes"] = extract_unique_vals(df_departments, "Code")
    keywords["department_names"] = extract_unique_vals(df_departments, "Name")
    keywords["instructor_names"] = clean_instructor_names(
        extract_unique_vals(df_instructors, "Name")
    )
    keywords["special_date_names"] = extract_unique_vals(df_dates, "Name")
    keywords["term_names"] = extract_unique_vals(df_terms, "Name")

    dumped = json.dumps(keywords, cls=NumpyEncoder)
    f = open("data/keywords.json", "w")
    f.write(dumped)
    f.close()

    sys.exit(0)

if __name__ == "__main__":
    main()