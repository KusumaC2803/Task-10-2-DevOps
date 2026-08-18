import time
import requests
from concurrent.futures import ThreadPoolExecutor

URL = "http://127.0.0.1:8000/dashboard"

def one(_):
    start = time.perf_counter()
    r = requests.get(URL, timeout=5)
    return (time.perf_counter() - start) * 1000, r.status_code

if __name__ == "__main__":
    count = 50
    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(one, range(count)))
    times = sorted(x[0] for x in results)
    p95 = times[int(len(times) * .95) - 1]
    print("requests=", count)
    print("workers=", 10)
    print("min_ms=", round(min(times), 2))
    print("avg_ms=", round(sum(times)/len(times), 2))
    print("p95_ms=", round(p95, 2))
    print("max_ms=", round(max(times), 2))
    print("success=", sum(1 for _, code in results if code == 200))
