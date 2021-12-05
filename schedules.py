import sys
import re
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

base_url = "https://schedules.calpoly.edu/"

# Given a container, return true iff the container has the specified attribute 
# and the attributes value matches the given pattern.
def attr_contains(cont, attr, pattern):
    if not cont.has_attr(attr):
        return False
    attr_vals = cont[attr]
    if not isinstance(attr_vals, list):
        attr_vals = [attr_vals]
    for val in attr_vals:
        if re.match(pattern, val):
            return True
    return False

# Given the soup for the schedules page with a list of classes for 
# a course, construct a table of classes with the following columns:
#   Name (PK) (FK to Courses) 
#   Section (PK)
#   Id (PK)
#   Type
#   Days
#   Start Time
#   End Time
#   Instructor (FK to Instructors)
#   Location (FK to Locations)
#   Enrollment Capacity
#   Enrollment Count
#   Waitlist Count
#   Drop Count
#   Term (PK) (FK to Terms)
def build_class_table(soup):
    column_names = [
        "Name", "Section", "Id", "Type", "Days", "Start Time",
        "End Time", "Instructor", "Location", "Enrollment Capacity",
        "Enrollment Count", "Waitlist Count", "Drop Count", "Term"
    ]
    df = pd.DataFrame(columns=column_names)

    if soup is None:
        return df

    term = soup.find("span", {"class": "term"}).get_text()

    table = soup.find("table")
    table_rows = table.find_all("tr")
    for row in table_rows:
        cells = row.find_all("td")
        # There should be 17 cells in a table row
        if len(cells) == 17:
            data = [cell.get_text() for cell in cells]

            # Remove overlap notation from the name
            data[0] = data[0].split("(")[0]
            # Remove GE
            data.pop(4)
            # Remove requirements
            data.pop(4)
            # Replace name cell with full name
            # NOTE: do not do this as the processor works around this
            # data[8] = row.find("td", {"class": "personName"}).find("a")["title"]
            # Remove location capacity
            data.pop(9)
            # Remove ICS
            data = data[:-1]
            # Replace non-breaking spaces with Nones
            data = [None if re.match("\xA0", d) else d for d in data]
            data.append(term)

            data = pd.Series(data)
            data.index = column_names
            df = df.append(data, ignore_index=True)

    df = df.drop_duplicates(subset=["Name", "Section", "Id", "Term"])
    df = df.set_index(["Name", "Section", "Id", "Term"])
    return df

# Given the soup for a schedules page with a list of courses for a 
# department, construct a table of courses with the following columns:
#   Id (PK)
#   Description
#   Type (PK)
#   GE
#   Requirements
#   Department (FK to Departments)
#   Term (PK) (FK to Terms)
def build_courses_table(soup):
    column_names = [
        "Id", "Description", "Type", "GE", "Requirements",
        "Department", "Term"
    ]
    df = pd.DataFrame(columns=column_names)

    term = soup.find("span", {"class": "term"}).get_text()

    table = soup.find("table")
    table_rows = table.find_all("tr")

    for row in table_rows:
        cells = row.find_all("td")
        # A row with no td cells is a header row. A row with only 1
        # td cell is a filler row that says no courses are available
        if len(cells) > 1:
            data = []
            for cell in cells:
                if attr_contains(cell, "class", "courseRequisites"):
                    span = cell.find("span")
                    if span is not None:
                        data.append(span["title"])
                    else:
                        data.append(cell.get_text())
                else:
                    data.append(cell.get_text())
            # Remove useless information from data.
            data = data[:6]
            data.pop(3)
            # Replace non-breaking spaces with Nones
            data = [None if re.match("\xA0", d) else d for d in data]
            data.append(data[0].split()[0])
            data.append(term)
            data = pd.Series(data)
            data.index = column_names
            df = df.append(data, ignore_index=True)

    df = df.drop_duplicates(subset=["Id", "Type", "Term"])
    df = df.set_index(["Id", "Type", "Term"])
    return df

# Given the soup for a schedules page with a list of departments in a
# college, contruct a table of departments with the following columns:
#   Code (PK)
#   Name
#   Catalog CIP Code
#   College (FK to Colleges)
#   Term (PK) (FK to Terms)
def build_department_table(soup):
    column_names = [
        "Code", "Name", "Catalog CIP Code", "College", "Term"
    ]
    df = pd.DataFrame(columns=column_names)

    college = soup.find("span", {"class": "alias"}).get_text().split("-")[1]
    term = soup.find("span", {"class": "term"}).get_text()

    table = soup.find("table")
    table_rows = table.find_all("tr")

    for row in table_rows:
        cells = row.find_all("td")
        if len(cells) > 0:
            data = [cell.get_text() for cell in cells]
            # Newer versions of the schedules page have a "Subject Phemeris" 
            # column. Remove it if it is there as it provides no codifiable
            # information.
            if len(data) == 4:
                data.pop(2)
            data.append(college)
            data.append(term)
            data = pd.Series(data)
            data.index = column_names
            df = df.append(data, ignore_index=True)

    df = df.set_index(["Code", "Term"])
    return df

# TODO
def build_college_table(soup):
    return

# Given the soup for the top level schedules page, construct a 
# table of courses with the following columns:
#   Id (PK)
#   Name 
#   Term Start
#   Term End
def build_term_table(soup):
    column_names = [
        "Id", "Name", "Term Start", "Term End",
    ]
    df = pd.DataFrame(columns=column_names)

    term_id = soup.find("span", {"class": "term"}).get_text()
    re_season = re.compile("term((Spring)|(Summer)|(Fall)|(Winter))")
    term_name = soup.find("span", {"class":  re_season}).get_text()
    term_date = soup.find("span", {"class": "termDate"}).get_text()
    
    toks = term_date.split(" to ")
    start_date = toks[0]
    end_date = toks[1]

    start_date = datetime.strptime(start_date, "%B %d, %Y").date()
    end_date = datetime.strptime(end_date, "%B %d, %Y").date()

    data = []
    data.append(term_id)
    data.append(term_name)
    data.append(start_date)
    data.append(end_date)
    data = pd.Series(data)
    data.index = column_names
    df = df.append(data, ignore_index=True)

    df = df.set_index(["Id"])
    return df

# Given the soup for a schedules page with a list of all locations,
# construct a table of locations with the following columns:
#   Id (PK)
#   Location Capacity
#   Name
#   Building Number
#   Room Number
#   Term (PK) (FK to Terms)
def build_locations_table(soup):
    column_names = [
        "Id", "Location Capacity", "Name", "Building Number",
        "Room Number", "Term"
    ]
    df = pd.DataFrame(columns=column_names)

    term = soup.find("span", {"class": "term"}).get_text()

    table = soup.find("table")
    table_rows = table.find_all("tr")

    building_name = ""
    for row in table_rows:
        headers = row.find_all("th")
        if len(headers) > 0:
            # If the table row is a divider then it has information about the
            # department. Save this information
            if attr_contains(headers[0], "class", "^divider.+"):
                building_name = headers[0].find(
                    "span", {"class": "locationDivDescr"}
                ).get_text()
        else:
            cells = row.find_all("td")
            data = [cell.get_text() for cell in cells]
            # From the data, keep only the id and the location capacity.
            data = [data[0]] + [data[2]]
            # Remove overlap information
            data[0] = data[0].split(" (")[0]
            data.append(building_name)
            toks = data[0].split("-")
            data.append(data[0].split("-")[0])
            if len(toks) > 1:
                data.append(data[0].split("-")[1])
            else:
                data.append(None)
            data.append(term)
            data = pd.Series(data)
            data.index = column_names
            df = df.append(data, ignore_index=True)

    df = df.drop_duplicates(subset=["Id", "Term"])
    df = df.set_index(["Id", "Term"])
    return df

# Given the soup for the schedules page with a list of useful
# dates, construct a table of special dates with the following
# columns:
#   Name
#   Start Date
#   End Date (None if event is one day only)
#   Is Campus Closed
#   Term (PK) (FK to Terms)
#   Id (PK)
def build_special_dates_table(soup):
    column_names = [
        "Name", "Start Date", "End Date", "Is Campus Closed", "Term", "Id"
    ]
    df = pd.DataFrame(columns=column_names)

    term = soup.find("span", {"class": "term"}).get_text()

    table = soup.find("table")
    table_rows = table.find_all("tr")

    running_id = 0
    for row in table_rows:
        cells = row.find_all("td")
        if len(cells) == 2:
            date = cells[0].get_text()
            name = cells[1].get_text()
            data = []

            name_toks = name.split(" - ")
            name = name_toks[0]
            data.append(name)

            date_toks = date.split(" thru ")
            start_date = date_toks[0]
            start_date = datetime.strptime(start_date, "%B %d, %Y (%A)").date()
            data.append(start_date)

            end_date = None
            if len(date_toks) > 1:
                end_date = date_toks[1].split(" - ")[0]
                end_date = datetime.strptime(end_date, "%B %d, %Y (%A)").date()
            data.append(end_date)

            is_campus_closed = False
            if len(name_toks) > 1:
                is_campus_closed = True
            data.append(is_campus_closed)

            data.append(term)
            data.append(running_id)
            running_id += 1

            data = pd.Series(data)
            data.index = column_names
            df = df.append(data, ignore_index=True)

    df = df.set_index(["Id", "Term"])
    return df

# Given the soup for a schedules page with the list of college instructors
# teaching by subject in a college, construct a table of instructors with 
# the following columns:
#   Name
#   Alias (PK)
#   Job Title 
#   Phone Number 
#   Office Location (FK to Locations)
#   Office Hours
#   Department (PK) (FK to Departments)
#   Term (PK) (FK to Terms)
def build_instructor_table(soup):
    column_names = [
        "Name", "Alias", "Job Title", "Phone Number", 
        "Office Location", "Office Hours", "Department", "Term"
    ]
    df = pd.DataFrame(columns=column_names)

    term = soup.find("span", {"class": "term"}).get_text()

    table = soup.find("table")
    table_rows = table.find_all("tr")

    department = ""
    for row in table_rows:
        headers = row.find_all("th")
        if len(headers) > 0:
            # If the table row is a divider then it has information about the
            # department. Save this information
            if attr_contains(headers[0], "class", "^divider.+"):
                # Divider text is of the form "CODE-NAME". Get just the code.
                department = headers[0].get_text().split("-")[0]
        else:
            cells = row.find_all("td")
            data = [cell.get_text() for cell in cells]
            # Replace non-breaking spaces with Nones
            data = [None if re.match("\xA0", d) else d for d in data]
            data.append(department)
            data.append(term)
            data = pd.Series(data)
            data.index = column_names
            df = df.append(data, ignore_index=True)

    df = df.drop_duplicates(subset=["Alias", "Department", "Term"])            
    df = df.set_index(["Alias", "Department", "Term"])
    return df

# Given the soup for a schedules page, get the links to the previous
# and next terms.
def get_temporal_links(soup):
    if soup is None:
        return []
    
    links = soup.find_all("a")
    
    output = []
    for a in links:
        spans = a.find_all("span")
        for span in spans:
            if attr_contains(span, "class", "(.+prev)|(.+next)"):
                output.append(base_url + a["href"])
    return output

# Given the soup for a schedules page, get the links on the page
# that match the given pattern
def get_links_by_name(soup, pattern):
    re_links = re.compile(pattern)
    links = soup.find_all("a", {"href":  re_links})
    links = [base_url + link["href"] for link in links]
    return links

# Given a url, return the corresponding soup
def get_soup(url):
    response = requests.get(url)
    if response.status_code != 200:
        if response.status_code == 404:
            return None
        else:
            print("Did not receive valid response from the server.")
            print("Got code " + str(response.status_code) + ". Exiting...")
            sys.exit(1)    
    return BeautifulSoup(response.content, "html.parser")

# Given a url for a schedules page and a function for building tables,
# aggregate the table for all terms into one large table
def aggregate_table(url, builder_func):
    soup = get_soup(url)
    df = builder_func(soup)
    traversed = [url]

    t_links = get_temporal_links(soup)
    while len(t_links) > 0:
        t_link = t_links.pop(0)
        print("\nWorking on t_link: " + t_link)
        t_soup = get_soup(t_link)
        df = df.append(builder_func(t_soup))
        traversed.append(t_link)

        new_t_links = get_temporal_links(t_soup)
        for new_t_link in new_t_links:
            if new_t_link not in traversed:
                t_links.append(new_t_link)

    df = df.sort_index()
    return df

# Given the url for the top level schedules page, get the links for
# each table of departments in a college. For each link, construct
# a temporal table and aggregate all the results together.
def aggregate_department_tables(url):
    soup = get_soup(url)
    df = pd.DataFrame()

    links = get_links_by_name(soup, "all_subject_.+\.htm")
    
    for link in links:
        print("\n=== Working on link: " + link)
        df = df.append(aggregate_table(link, build_department_table))

    return df

# Given the url for the top level schedules page, get the links for
# each table of instructors in a college. For each link, construct
# a temporal table and aggregate all the results together.
def aggregate_instructor_tables(url):
    soup = get_soup(url)
    df = pd.DataFrame()

    links = get_links_by_name(soup, "all_person_.+\.htm")
    
    for link in links:
        print("\n=== Working on link: " + link)
        df = df.append(aggregate_table(link, build_instructor_table))

    return df

# Given the url for the top level schedules page, get each page of departments
# in a college. For each department page, get the links for each table of 
# courses. For each link, construct a temporal table and aggregate all the 
# results together.
def aggregate_course_tables(url):
    soup = get_soup(url)
    df = pd.DataFrame()

    department_links = get_links_by_name(soup, "all_subject_.+\.htm")

    course_links = []
    for d_link in department_links:
        d_soup = get_soup(d_link)
        course_links.extend(get_links_by_name(d_soup, "courses_.+\.htm"))
    
    for c_link in course_links:
        print("\n=== Working on link: " + c_link)
        df = df.append(aggregate_table(c_link, build_courses_table))

    return df

# Given the url for the top level schedules page, get each page of departments
# in a college. For each department page, get the links for each table of 
# courses. For each course page, get the links for each table of classes. For 
# each link, construct a temporal table and aggregate all the results together.
def aggregate_class_tables(url):
    soup = get_soup(url)
    df = pd.DataFrame()

    department_links = get_links_by_name(soup, "all_subject.+\.htm")

    course_links = []
    for d_link in department_links:
        d_soup = get_soup(d_link)
        course_links.extend(get_links_by_name(d_soup, "courses_.+\.htm"))
    
    class_links = []
    for co_link in course_links:
        co_soup = get_soup(co_link)
        class_links.extend(get_links_by_name(co_soup, "classes_.+\.htm"))
    
    for cl_link in class_links:
        print("\n=== Working on link: " + cl_link)
        df = df.append(aggregate_table(cl_link, build_class_table))

    return df

def main():
    print("\nBuilding class table...")
    class_tables = aggregate_class_tables("https://schedules.calpoly.edu/")   
    f = open("data/classes.csv", "w")
    f.write(class_tables.to_csv())
    f.close()

    print("\nBuilding course table...")
    course_tables = aggregate_course_tables("https://schedules.calpoly.edu/")   
    f = open("data/courses.csv", "w")
    f.write(course_tables.to_csv())
    f.close()

    print("\nBuilding department table...")
    department_tables = aggregate_department_tables("https://schedules.calpoly.edu/")   
    f = open("data/departments.csv", "w")
    f.write(department_tables.to_csv())
    f.close()

    print("\nBuilding instructor table...")
    instructor_tables = aggregate_instructor_tables("https://schedules.calpoly.edu/")   
    f = open("data/instructors.csv", "w")
    f.write(instructor_tables.to_csv())
    f.close()

    print("\nBuilding term table...")
    term_table = aggregate_table("https://schedules.calpoly.edu/index_curr.htm", build_term_table)   
    f = open("data/terms.csv", "w")
    f.write(term_table.to_csv())
    f.close()

    print("\nBuilding location table...")
    location_table = aggregate_table(
        "https://schedules.calpoly.edu/all_location_curr.htm", build_locations_table
    )   
    f = open("data/locations.csv", "w")
    f.write(location_table.to_csv())
    f.close()

    print("\nBuilding special dates table...")
    date_table = aggregate_table(
        "https://schedules.calpoly.edu/dates_curr.htm", build_special_dates_table
    )   
    date_table.reset_index()
    f = open("data/special_dates.csv", "w")
    f.write(date_table.to_csv())
    f.close()

if __name__ == "__main__":
    main()





