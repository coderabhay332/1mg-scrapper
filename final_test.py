from extractor import extract_medicine_details
import time

url = "https://www.1mg.com/drugs/augmentin-625-duo-tablet-138629"

t0 = time.time()
result = extract_medicine_details(url)
t1 = time.time()

print(f"Extraction took: {t1-t0:.2f}s")
print()
skip = {"False", "{}", "[]", '"[]"', '"{}"'}
for key, val in result.items():
    sval = str(val)
    if val and sval not in skip:
        preview = sval[:90].replace("\n", " ")
        print(f"  {key:<26}: {preview}")
    else:
        print(f"  {key:<26}: (empty)")
