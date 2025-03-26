# capture_service.py
import os
from datetime import datetime
import pyzed.sl as sl
import logging

class CaptureService:
    def __init__(self, output_dir):
        self.cam = sl.Camera()
        self.init_params = sl.InitParameters(
            depth_mode=sl.DEPTH_MODE.NEURAL_PLUS,
            coordinate_units=sl.UNIT.MILLIMETER,
            coordinate_system=sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP,
            camera_resolution=sl.RESOLUTION.HD1200,
            camera_fps=60,
            async_image_retrieval=False
        )
        status = self.cam.open(self.init_params)
        if status != sl.ERROR_CODE.SUCCESS:
            raise RuntimeError(f"Unable to open camera: {status}")
        self.recording = False
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        logging.info("Camera opened successfully.")

    def start_capture(self):
        if not self.recording:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_filename = os.path.join(self.output_dir, f"{timestamp}.svo2")
            rec_params = sl.RecordingParameters(output_filename, sl.SVO_COMPRESSION_MODE.H265)
            err = self.cam.enable_recording(rec_params)
            if err != sl.ERROR_CODE.SUCCESS:
                raise RuntimeError(f"Error enabling recording: {err}")
            self.recording = True
            logging.info("Recording started: %s", output_filename)
            return output_filename

    def stop_capture(self):
        if self.recording:
            self.cam.disable_recording()
            self.recording = False
            logging.info("Recording stopped.")

    def close_camera(self):
        self.cam.close()
        logging.info("Camera closed.")
