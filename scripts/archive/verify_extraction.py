import json, re, glob, os, sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

def get_grade_info(total, max_tot, is_pass=True):
    if not is_pass or total is None or total < (max_tot * 0.40):
        return "F", 0
    pct = (total / max_tot) * 100.0
    if pct >= 90.0:
        return "O", 10
    elif pct >= 80.0:
        return "A+", 9
    elif pct >= 70.0:
        return "A", 8
    elif pct >= 60.0:
        return "B+", 7
    elif pct >= 55.0:
        return "B", 6
    elif pct >= 50.0:
        return "C", 5
    elif pct >= 40.0:
        return "D", 4
    else:
        return "F", 0

print("Grade function test:")
for m, mt in [(40, 50), (45, 50), (22, 50), (61, 75), (75, 100), (84, 100), (67, 100), (44, 50), (43, 50), (68, 100), (44, 50), (45, 50), (45, 50)]:
    g, gp = get_grade_info(m, mt)
    print(f"  {m}/{mt} ({m/mt*100:.1f}%) -> Grade: {g:2s} GP: {gp}")
