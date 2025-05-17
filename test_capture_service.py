# test_capture_service_diff.py

import logging
import os
import time
from capture_service import CaptureService

# 1) Enable logging so we see start/stop messages
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s: %(message)s")

# 2) Point to your output folder
OUTPUT = "/home/user/Desktop/double_captures"
os.makedirs(OUTPUT, exist_ok=True)

# 3) Instantiate service
svc = CaptureService(OUTPUT)

# 4) Snapshot preexisting .svo / .svo2 files
preexisting = {
    f for f in os.listdir(OUTPUT)
    if f.lower().endswith((".svo", ".svo2"))
}
logging.info("Preexisting files: %s", sorted(preexisting))

# 5) Start recording
logging.info("Calling start_capture()…")
ok = svc.start_capture()
logging.info("start_capture() returned %s", ok)
if not ok:
    logging.error("Recorder failed to start – aborting test.")
    exit(1)

# 6) Wait a bit (make sure it’s longer than 1 second)
RECORD_SECONDS = 10
logging.info("Recording for %d seconds…", RECORD_SECONDS)
time.sleep(RECORD_SECONDS)

# 7) Stop recording
logging.info("Stopping capture…")
svc.stop_capture()

# 8) Diff and print new files + sizes
all_caps = {
    f for f in os.listdir(OUTPUT)
    if f.lower().endswith((".svo", ".svo2"))
}
new_caps = sorted(all_caps - preexisting)
if not new_caps:
    logging.error("No new .svo/.svo2 files appeared!")
else:
    logging.info("New capture files:")
    for fname in new_caps:
        path = os.path.join(OUTPUT, fname)
        size = os.path.getsize(path)
        logging.info("  %s   %d bytes", fname, size)
