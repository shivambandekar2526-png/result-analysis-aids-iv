import subprocess, time, os

ranges = [
    (0, 12),
    (12, 24),
    (24, 36),
    (36, 47)
]

print("Launching 4 worker subprocesses...")
procs = []
for s, e in ranges:
    p = subprocess.Popen([r"python", "-u", "worker.py", str(s), str(e)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    procs.append((s, e, p))

for s, e, p in procs:
    for line in p.stdout:
        print(line, end="", flush=True)
    p.wait()

print("All OCR workers completed successfully!")
