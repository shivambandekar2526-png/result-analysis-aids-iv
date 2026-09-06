# src/config.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_PATH = os.path.join(DATA_DIR, "raw", "AI&DS_SEM4_RESULTS.pdf")
PROCESSED_DATA_PATH = os.path.join(DATA_DIR, "processed", "AI_DS_SEM4_MASTER_RESULTS.csv")
CACHE_DIR = os.path.join(DATA_DIR, "cache", "ocr_cache")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
FIGURES_DIR = os.path.join(REPORTS_DIR, "figures")

SUBJECTS = [
    {
        "code": "1313311", "prefix": "OE", "name": "Administrative Policy of Chhatrapati Shivaji Maharaja",
        "type": "THEORY", "max_ext": 30, "min_ext": 12, "max_int": 20, "min_int": 8, "max_tot": 50, "credits": 2
    },
    {
        "code": "2014411", "prefix": "MINIPROJ", "name": "Mini Project",
        "type": "TW_ORAL", "max_tw": 50, "min_tw": 20, "max_oral": 25, "min_oral": 10, "max_tot": 75, "credits": 2
    },
    {
        "code": "2114111", "prefix": "CT", "name": "Computational Theory",
        "type": "THEORY", "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "credits": 3
    },
    {
        "code": "2114112", "prefix": "DBMS", "name": "Database Management System",
        "type": "THEORY", "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "credits": 3
    },
    {
        "code": "2114113", "prefix": "OS", "name": "Operating System",
        "type": "THEORY", "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "credits": 3
    },
    {
        "code": "2114114", "prefix": "DBMS_LAB", "name": "Database Management System Lab",
        "type": "TW_ORAL", "max_tw": 25, "min_tw": 10, "max_oral": 25, "min_oral": 10, "max_tot": 50, "credits": 1
    },
    {
        "code": "2114115", "prefix": "OS_LAB", "name": "Operating System Lab",
        "type": "TW_ORAL", "max_tw": 25, "min_tw": 10, "max_oral": 25, "min_oral": 10, "max_tot": 50, "credits": 1
    },
    {
        "code": "2304211", "prefix": "FTS", "name": "Fundamentals of Telecommunication Systems",
        "type": "THEORY", "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "credits": 3
    },
    {
        "code": "2304212", "prefix": "TC_LAB", "name": "Basic Telecommunication Experiments",
        "type": "TW_ORAL", "max_tw": 25, "min_tw": 10, "max_oral": 25, "min_oral": 10, "max_tot": 50, "credits": 1
    },
    {
        "code": "2994511", "prefix": "BMD", "name": "Business Model Development",
        "type": "TW_ONLY", "max_tw": 50, "min_tw": 20, "max_tot": 50, "credits": 2
    },
    {
        "code": "2994512", "prefix": "DT", "name": "Design Thinking",
        "type": "TW_ONLY", "max_tw": 50, "min_tw": 20, "max_tot": 50, "credits": 2
    }
]

MAX_MARKS = 775
TOTAL_CREDITS = 23
