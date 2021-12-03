import sys
import numpy as np
import pandas as pd

def extract_unique_vals(df, col):
    return df[col].unique()

def main():
    # Load tables
    df_classes = pd.read_csv("classes.csv", encoding="ISO-8859-1")
    df_courses = pd.read_csv("courses.csv", encoding="ISO-8859-1")
    df_departments = pd.read_csv("departments.csv", encoding="ISO-8859-1")
    df_instructors = pd.read_csv("instructors.csv", encoding="ISO-8859-1")
    df_locations = pd.read_csv("locations.csv")
    df_dates = pd.read_csv("special_dates.csv")
    df_terms = pd.read_csv("terms.csv")

    # Verify df indices
    # df_classes.set_index(["Name", "Section", "Id", "Term"], inplace=True, verify_integrity=True)
    # df_courses.set_index(["Id", "Type", "Term"], inplace=True, verify_integrity=True)
    # df_departments.set_index(["Code", "Term"], inplace=True, verify_integrity=True)
    # df_instructors.set_index(["Alias", "Department", "Term"], inplace=True, verify_integrity=True)
    # df_locations.set_index(["Id", "Term"], inplace=True, verify_integrity=True)
    # df_dates.set_index(["Id", "Term"], inplace=True, verify_integrity=True)
    # df_terms.set_index("Id", inplace=True, verify_integrity=True)

    sys.exit(0)

if __name__ == "__main__":
    main()