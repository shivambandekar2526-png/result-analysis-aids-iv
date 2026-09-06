import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

from test_master_pipeline import SUBJECTS
from run_master_extraction import extract_full_student_record

targets = [
    (5, "101410028"),
    (12, "101410042"),
    (32, "101410081"),
    (34, "101410085"),
    (36, "101410926"),
    (37, "101410928")
]

for p, seat in targets:
    with open(f"ocr_cache/page_{p:03d}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    boxes = data["boxes"]
    sb = [b for b in boxes if seat in b["text"]][0]
    rec = extract_full_student_record(p, sb, boxes)
    print(f"\n==================== Page {p} Seat {seat} ({rec['name']}) ====================")
    print(f"PDF Overall Total: {rec['overall_total']}")
    tot_sum = 0
    for s in SUBJECTS:
        pfx = s["prefix"]
        st = s["type"]
        ext = rec.get(f"{pfx}_external")
        int_m = rec.get(f"{pfx}_internal")
        tw = rec.get(f"{pfx}_term_work")
        oral = rec.get(f"{pfx}_oral")
        tot = rec.get(f"{pfx}_total")
        g = rec.get(f"{pfx}_grade")
        if tot is not None: tot_sum += tot
        print(f"  {pfx:10s} -> Ext={ext} Int={int_m} TW={tw} Oral={oral} => Tot={tot} Grade={g}")
    print(f"Sum of extracted totals: {tot_sum} (Diff from PDF: {rec['overall_total'] - tot_sum})")
