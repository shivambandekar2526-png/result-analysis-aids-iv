import json, re, glob, os, sys
sys.stdout.reconfigure(encoding="utf-8")

def parse_student_blocks(data):
    boxes = data["boxes"]
    # Group boxes into student records by looking at seat numbers or ERN numbers
    # Each page may have 1 or 2 students
    # Find all seat number boxes: 9 digits starting with 1014
    seat_boxes = []
    for b in boxes:
        # Match seat numbers like 101410022 or similar 9 digit numbers
        if re.search(r"\b1014\d{5}\b", b["text"]):
            seat_boxes.append(b)
            
    seat_boxes.sort(key=lambda b: b["ymin"])
    return len(seat_boxes), [b["text"] for b in seat_boxes]

files = sorted(glob.glob("ocr_cache/page_*.json"))
total_students = 0
for fpath in files:
    page_num = int(re.search(r"page_(\d+)", fpath).group(1))
    if page_num in [0, 1]: # legend
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)
    n, seats = parse_student_blocks(data)
    total_students += n
    print(f"Page {page_num:02d}: {n} students -> {seats}")

print(f"\nTotal students across {len(files)-2} parsed pages: {total_students}")
