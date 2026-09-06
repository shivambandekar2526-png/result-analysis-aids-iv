import json, re, glob, os, sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

def parse_mark_token(t, max_val):
    if not t:
        return None
    t = str(t).strip()
    # Absent
    if any(w in t.upper() for w in ["ABS", "AA", "AB", "NULL"]):
        return 0
    # Grace mark like "20 *4" or "20*4"
    if "*" in t:
        parts = re.findall(r"\d+", t)
        if len(parts) >= 2:
            return int(parts[0]) + int(parts[1])
        elif len(parts) == 1:
            return int(parts[0])
            
    # Prefixed tokens like "E1 24", "E124", "I1 16", "I116", "1117", "11 17", "T1 42", "T142", "O1 19", "O119", "TOT 40", "TOT40"
    m = re.search(r"(?:E1|I1|11|l1|T1|O1|01|TOT)\s*(\d{1,2})\b", t, re.I)
    if m:
        v = int(m.group(1))
        if v <= max_val:
            return v
            
    # Handle "1116", "1117", "1106" where 11 is I1
    if re.match(r"^11\d{1,2}$", t):
        v = int(t[2:])
        if v <= max_val:
            return v
            
    # Find all integers
    nums = re.findall(r"\b\d+\b", t)
    if nums:
        # Prefer the last number that is <= max_val
        for n_str in reversed(nums):
            v = int(n_str)
            if v <= max_val:
                return v
    return None

print("Testing parse_mark_token:")
for token, max_v in [
    ("E1 24", 30), ("E124", 30), ("I116", 20), ("1117", 20), ("11 17", 20),
    ("20 *4", 60), ("TOT 40", 50), ("TOT40", 50), ("34", 50), ("0.0 21", 25),
    ("ABS", 60), ("AA", 40), ("1108", 20), ("E1 20 *4", 60)
]:
    print(f"  '{token}' (max {max_v}) -> {parse_mark_token(token, max_v)}")
