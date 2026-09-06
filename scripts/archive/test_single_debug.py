import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

from test_deep_pipeline import parse_student_deep, SUBJECTS

with open("ocr_cache/page_003.json", "r", encoding="utf-8") as f:
    data = json.load(f)
boxes = data["boxes"]
sb = [b for b in boxes if "101410023" in b["text"]][0]
rec = parse_student_deep(3, sb, boxes)

for s in SUBJECTS:
    pfx = s["prefix"]
    print(f"{pfx:10s} -> Ext={rec.get(pfx+'_external')} Int={rec.get(pfx+'_internal')} TW={rec.get(pfx+'_term_work')} Oral={rec.get(pfx+'_oral')} Tot={rec.get(pfx+'_total')} Grade={rec.get(pfx+'_grade')}")
print("Sum of subject totals:", sum(rec[s['prefix']+'_total'] for s in SUBJECTS if rec[s['prefix']+'_total'] is not None))
print("PDF overall total:", rec["overall_total"])
