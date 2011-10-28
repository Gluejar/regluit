import mechanize
import csv
import HTMLParser
import argparse

h = HTMLParser.HTMLParser()

# parse options

parser = argparse.ArgumentParser(description='Download and parse LibraryThing booklist.')
parser.add_argument('user', help='LibraryThing username')
parser.add_argument('password', help='LibraryThing password')

args = parser.parse_args()

USERNAME = args.user
PW = args.password

LT_url = "https://www.librarything.com"
LT_csv_file_url = "http://www.librarything.com/export-csv"

def retrieve_book_list(user,password):
    br = mechanize.Browser()
    br.open(LT_url)
    # select 2 form
    br.select_form(nr=1)
    br["formusername"] = user
    br["formpassword"] = password
    br.submit()
    
    # get CSV file
    response = br.open(LT_csv_file_url)
    return response

def parse_csv(f):
    reader = csv.DictReader(f)
    for (i,row) in enumerate(reader):
        print i, h.unescape(row["'TITLE'"]), h.unescape(row["'AUTHOR (first, last)'"]), row["'ISBNs'"], row["'COMMENT'"], row["'TAGS'"], row["'COLLECTIONS'"], h.unescape(row["'REVIEWS'"])
    
if __name__ == '__main__':
    dynamic = True
    if dynamic:
        f = retrieve_book_list(USERNAME, PW)
    else:
        fname = "/Users/raymondyee/Downloads/LibraryThing_export.csv"
        f = open(fname,"rb")
    parse_csv(f)     