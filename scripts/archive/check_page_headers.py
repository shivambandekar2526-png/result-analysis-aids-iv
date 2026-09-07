import json

for p in [4, 9, 16, 18, 19, 21, 23, 26, 28, 31, 32, 36, 37, 45, 47]:
    fn = f'data/cache/ocr_cache/page_{p-1:03d}.json'
    with open(fn, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"\n=== PAGE {p} ===")
    for b in data['boxes']:
        txt = b['text']
        if any(k in txt.upper() for k in ['TERNA', 'MU-', 'MU03', 'COLLEGE', 'TRUST', 'ERN', 'GENDER', '0237']):
            print(f"   y=[{b['ymin']:.1f}-{b['ymax']:.1f}] x=[{b['xmin']:.1f}-{b['xmax']:.1f}] txt='{txt}'")
