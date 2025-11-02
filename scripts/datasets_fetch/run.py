from cyberghost_vpn_ip_fetch import run as cyberghost_run
from cipher_suite_fetch import run as cipher_suite_run
from mullvad_vpn_ip_fetch import fetch_file as mullvad_run
from nord_vpn_ip_fetch import fetch_file as nord_run
from proton_vpn_ip_fetch import run as proton_run
from surfshark_vpn_ip_list import fetch_file as surfshark_run
from tlds_fetch import run as tlds_run
from tor_guard_and_exit_nodes_ip_fetch import fetch_tor_lists as tor_run
import concurrent.futures
import time
from datetime import datetime, UTC

TASKS = [
    ("CyberGhost", cyberghost_run),
    ("CipherSuite", cipher_suite_run),
    ("Mullvad", mullvad_run),
    ("Nord", nord_run),
    ("Proton", proton_run),
    ("Surfshark", surfshark_run),
    ("TLDs", tlds_run),
    ("TorGuard", tor_run),
]

def run_all_parallel(max_workers: int | None = None, per_task_timeout: float | None = None):
    """
    Run all TASKS in parallel using threads.

    - max_workers: None -> ThreadPoolExecutor default (min(32, os.cpu_count() + 4)).
                   You can set an int to limit concurrency.
    - per_task_timeout: seconds to wait for each task result (None disables).
    """
    start_all = time.time()
    print(f"[{datetime.utcnow().isoformat()}Z] Starting {len(TASKS)} fetchers (max_workers={max_workers})")

    # Submit tasks
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_name = {
            executor.submit(func): name for (name, func) in TASKS
        }

        completed = 0
        for future in concurrent.futures.as_completed(future_to_name):
            name = future_to_name[future]
            task_start = time.time()
            try:
                result = future.result(timeout=per_task_timeout)
                elapsed = time.time() - task_start
                print(f"[✓] {name} completed in {elapsed:.2f}s")
            except concurrent.futures.TimeoutError:
                print(f"[!] {name} timed out after {per_task_timeout}s")
            except Exception as exc:
                print(f"[x] {name} raised exception: {exc!r}")
            completed += 1

    total_elapsed = time.time() - start_all
    print(f"[{datetime.now(UTC).isoformat()}] All done. {completed}/{len(TASKS)} finished. Total elapsed: {total_elapsed:.2f}s")


if __name__ == "__main__":
    # Example: limit to 6 threads and give each task 180s to finish
    run_all_parallel(max_workers=6, per_task_timeout=180)
