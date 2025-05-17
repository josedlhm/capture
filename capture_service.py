# capture_service.py

import os
import subprocess
import signal
import logging
import time

class CaptureService:
    RECORDER_BIN = "/home/user/Desktop/two_cameras/build/ZED_SVO_Recording_Multi"

    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.recording = False
        self._proc = None

    def start_capture(self) -> bool:
        if self.recording:
            logging.warning("Already recording!")
            return False

        cmd = [CaptureService.RECORDER_BIN, self.output_dir]
        logging.info("Starting recorder: %s", cmd)
        try:
            self._proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )
        except Exception as e:
            logging.error("Failed to start recorder: %s", e)
            return False

        # give it a moment to decide whether it can run
        time.sleep(1.0)
        exit_code = self._proc.poll()
        if exit_code is not None:
            out_bytes, err_bytes = self._proc.communicate()
            # print raw bytes so nothing is swallowed:
            print("=== RECORDER STDOUT ===")
            print(out_bytes)
            print("=== RECORDER STDERR ===")
            print(err_bytes)
            logging.error("Recorder exited with code %d", exit_code)
            self._proc = None
            return False

        self.recording = True
        return True

    def stop_capture(self) -> None:
        if not self._proc:
            return
        # cleanly stop all ZEDs in the C++ process
        os.killpg(os.getpgid(self._proc.pid), signal.SIGINT)
        self._proc.wait(timeout=5)
        self._proc = None
        self.recording = False

    def close_camera(self) -> None:
        if self.recording:
            self.stop_capture()
