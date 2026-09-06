import json, glob, re, sys
sys.stdout.reconfigure(encoding="utf-8")

# Let's inspect each student's subject columns
# On each student block:
# Top block (Student 1): header subject codes are around y=250-420, marks around y=420-640
# Bottom block (Student 2): header subject codes are around y=640-820, marks around y=820-1050

all_student_subjects = []

for p in range(2, 47):
    with open(f"ocr_cache/page_{p:03d}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    boxes = data["boxes"]
    
    # find seat numbers
    seat_boxes = [b for b in boxes if re.search(r"\b1014\d{5}\b", b["text"])]
    seat_boxes.sort(key=lambda b: b["ymin"])
    
    for s_idx, sb in enumerate(seat_boxes):
        seat = re.search(r"\b1014\d{5}\b", sb["text"]).group(0)
        s_y = sb["ymin"]
        
        # Determine y range for this student
        if s_idx == 0 and len(seat_boxes) == 2:
            # top student
            hdr_ymin, hdr_ymax = 200, min(500, s_y)
            blk_ymin, blk_ymax = 200, (seat_boxes[1]["ymin"] - 50)
        elif s_idx == 1:
            # bottom student
            hdr_ymin, hdr_ymax = (seat_boxes[0]["ymin"] + 50), min(900, s_y)
            blk_ymin, blk_ymax = (seat_boxes[0]["ymin"] + 50), 1200
        else:
            # single student page (page 2 or page 46)
            hdr_ymin, hdr_ymax = 200, min(600, s_y)
            blk_ymin, blk_ymax = 200, 1200
            
        # Get all subject codes in this header range
        subj_boxes = [b for b in boxes if hdr_ymin <= b["ymin"] <= hdr_ymax and re.match(r"^\d{7}$", b["text"])]
        subj_boxes.sort(key=lambda b: b["xmin"])
        codes = [b["text"] for b in subj_boxes]
        
        all_student_subjects.append({
            "page": p,
            "seat": seat,
            "num_subjects": len(codes),
            "codes": codes
        })

print(f"Total students processed: {len(all_student_subjects)}")
distinct_combinations = set()
distinct_codes = set()
for s in all_student_subjects:
    distinct_combinations.add(tuple(s["codes"]))
    for c in s["codes"]:
        distinct_codes.add(c)

print(f"Total distinct subject codes across all students: {len(distinct_codes)} -> {sorted(distinct_codes)}")
print(f"Total distinct curriculum schemes/combinations: {len(distinct_combinations)}")
for comb in sorted(distinct_combinations):
    print("  ", comb)
