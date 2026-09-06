import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

from check_discrepancies import test_students, extract_student_marks, SUBJECTS_INFO

for p, sb, boxes in test_students:
    seat = re.search(r"\b1014\d{5}\b", sb["text"]).group(0)
    if seat in ["101410023", "101410024"]:
        s_y = sb["ymin"]
        s_marks = extract_student_marks(boxes, s_y)
        print(f"=== Seat {seat} (Page {p}) ===")
        for subj in SUBJECTS_INFO:
            pfx = subj["prefix"]
            stype = subj["type"]
            if stype == "THEORY":
                print(f"  {pfx:10s} (THEORY): Ext={s_marks[f'{pfx}_external']} Int={s_marks[f'{pfx}_internal']} -> Tot={s_marks[f'{pfx}_total']} Grade={s_marks[f'{pfx}_grade']}")
            elif stype == "TW_ORAL":
                print(f"  {pfx:10s} (TW+ORAL): TW={s_marks[f'{pfx}_term_work']} Oral={s_marks[f'{pfx}_oral']} -> Tot={s_marks[f'{pfx}_total']} Grade={s_marks[f'{pfx}_grade']}")
            elif stype == "TW_ONLY":
                print(f"  {pfx:10s} (TW_ONLY): TW={s_marks[f'{pfx}_term_work']} -> Tot={s_marks[f'{pfx}_total']} Grade={s_marks[f'{pfx}_grade']}")
