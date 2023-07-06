import cv2
import numpy as np
import datetime as dt
from time import perf_counter
from typing import Optional
from .base import DepthEstimator


class DepthCamera:
    """
    Depth-scanning camera architecture.

    This class represents a depth-scanning camera architecture that captures frames from a video source,
    applies depth estimation to the frames, and displays them on the screen. It provides functionality
    to control the depth estimation mode, color mapping, and scale factor of the displayed frames.

    Attributes:
        camera_num (int): The camera number to use (default is 0).
        camera (cv2.VideoCapture): The OpenCV VideoCapture object representing the camera.
        is_running (bool): Flag indicating if the camera is running.
        __scale (float): Private attribute, the scale factor for the displayed frames.
        estimator (DepthEstimator): The depth estimation module.
    """
    def __init__(self, camera: Optional[int] = 0, mode: Optional[str] = "standard", scale: Optional[float] = 1.0, color: Optional[str] = "hot"):
        """
        Initialize the DepthCamera object.

        Args:
            camera (int, optional): Camera number. Defaults to 0.
            mode (str, optional): Mode of depth estimation. Defaults to "standard".
            scale (float, optional): Scale factor for window display. Defaults to 1.0.
            color (str, optional): Color mapping. Defaults to "hot".
        """
        self.camera_num = camera
        self.camera = cv2.VideoCapture(self.camera_num)
        self.is_running = False
        self.__scale = scale
        self.estimator = DepthEstimator(mode=mode, color=color)
        print(f'Starting up depth scanner, running {mode} mode and using {color} mapping.')

    def __repr__(self) -> str:
        return f'<DepthCamera | camera={self.camera_num}, device={str(self.estimator.device).upper()}>'

    @property
    def scale(self) -> float:
        """
        Returns the scale factor of the window display.
        """
        return self.__scale

    @scale.setter
    def set_scale(self, new_scale_factor: float) -> None:
        """
        Set the scale factor of the window display.

        Args:
            new_scale_factor (float): New scale factor
        """
        self.__scale = new_scale_factor

    @staticmethod
    def __resize(image, factor: Optional[float] = 1.0) -> np.ndarray:
        """
        Scale an image evenly by a given factor.

        Args:
            image (np.ndarray): Image to scale
            factor (float, optional): Scaling factor. Defaults to 1.

        Returns:
            np.ndarray: Rescaled image
        """
        height, width, _ = image.shape
        new_dimensions = (round(width * factor), round(height * factor))
        return cv2.resize(image, new_dimensions, interpolation=cv2.INTER_AREA)

    def capture(self, frame: np.ndarray) -> None:
        """
        Capture a camera frame and render a depth map.

        Args:
            frame (np.ndarray): Camera capture frame
        """
        colored_map = self.estimator.colormap(frame)  # Preprocess frame

        # Display colored depth map
        date_today = dt.datetime.now().strftime("%d %B %Y")
        timestamp = dt.datetime.now().strftime("%H:%M:%S")
        print(f'[{date_today} | {timestamp}] Frame captured!')
        cv2.imshow(f'Depth Scan - {timestamp}', colored_map)

    def run(self) -> None:
        """
        Run the video camera.
        """
        self.is_running = True
        print(f'[{self.estimator.device.upper()}] Running depth scan...')

        try:
            while self.is_running:
                frame_start_time = perf_counter()
                ret, frame = self.camera.read()
                display_frame = self.estimator.colormap(frame) if self.estimator.live_render else frame
                frame_end_time = perf_counter()
                fps = round(1 / (frame_end_time - frame_start_time))
                window_label = "Depth Capture" if self.estimator.live_render else "Standard Camera"
                cv2.putText(display_frame, f'FPS: {fps}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (10, 255, 100), 2)
                cv2.imshow(window_label, self.__resize(display_frame, factor=self.scale))

                key = cv2.waitKey(10)
                if key == 32 and not self.estimator.live_render:
                    self.capture(frame)  # Capture frame on spacebar press
                if key == 27 or key == ord("q"):
                    print("Closing scanner...")  # Close windows when Esc or 'Q' is pressed
                    self.is_running = False
                    break

        except Exception as e:
            print(f'Error during camera streaming: {e}')

        finally:
            self.camera.release()
            cv2.destroyAllWindows()

        print("Scanner closed!")
