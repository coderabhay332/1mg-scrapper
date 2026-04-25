import cProfile
from extractor import extract_medicine_details
import sys

def main():
    url = "https://www.1mg.com/drugs/augmentin-625-duo-tablet-138629"
    cProfile.runctx("extract_medicine_details(url)", globals(), locals(), sort="cumtime")

if __name__ == "__main__":
    main()
