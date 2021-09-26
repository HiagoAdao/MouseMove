# Hiago Oliveira e Isaura Koch
# Trabalho G1 - Computação Gráfica, IMED
import cv2
import numpy as np
import pyautogui
from typing import Callable, Tuple
from time import sleep


class MouseMove:
    def __init__(self, cam_position: int):
        self.__cam = cv2.VideoCapture(cam_position)

        self.__blue_hsv = (
            np.array([97, 100, 117]),  # Lower
            np.array([117, 255, 255]),  # Upper
        )
        self.__green_hsv = (
            np.array([46, 99, 132]),  # Lower
            np.array([66, 255, 255])  # Upper
        )
        self.__purple_hsv = (
            np.array([117, 21, 150]),  # Lower
            np.array([179, 255, 255])  # Upper
        )
        self.__yellow_hsv = (
            np.array([5, 125, 209]),  # Lower
            np.array([40, 255, 255])  # Upper
        )

        self.__commands = dict(
            cursor_follow_color=self.__cursor_follow_color_command,
            left_button=self.__left_button_command,
            right_button=self.__right_button_command,
            double_click=self.__double_click_command,
            stop_execution=self.__stop_execution_command,
            last_command_used=None
        )
        self.__mouse_position = pyautogui.position()

    def run(self) -> None:
        is_running = bool(
            self.__commands['last_command_used'] !=
            self.__stop_execution_command.__name__
        )
        while is_running:
            _, frame = self.__cam.read()
            frame = cv2.flip(frame, 1)
            command: Callable = self.__get_command_by_color_in_frame(frame)

            command and command()
            self.__commands['last_command_used'] = command and command.__name__

            print(
                '[INFO] '
                f"Last Command Used: {self.__commands['last_command_used']}"
            )

            cv2.imshow("Camera", frame)

            stop_execution = bool(
                cv2.waitKey(1) == ord('q') or
                self.__commands['stop_execution'].__name__ ==
                self.__commands['last_command_used']
            )
            if stop_execution:
                sleep(0.5)
                break

    def __get_command_by_color_in_frame(self, frame) -> Callable:
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        has_blue_in_frame, _ = self.__identify_color(
            frame,
            hsv_frame,
            self.__blue_hsv
        )
        has_green_in_frame, position = self.__identify_color(
            frame,
            hsv_frame,
            self.__green_hsv
        )
        has_yellow_in_frame, _ = self.__identify_color(
            frame,
            hsv_frame,
            self.__yellow_hsv
        )
        has_purple_in_frame, _ = self.__identify_color(
            frame,
            hsv_frame,
            self.__purple_hsv
        )

        is_double_click = bool(
            has_purple_in_frame and
            has_yellow_in_frame and
            'double_click' != self.__commands['last_command_used']
        )
        is_right_button = bool(
            has_purple_in_frame and
            'right_button' != self.__commands['last_command_used']
        )
        is_left_button = bool(
            has_yellow_in_frame and
            'left_button' != self.__commands['last_command_used']
        )
        if is_double_click:
            return self.__commands['double_click']
        elif is_right_button:
            return self.__commands['right_button']
        elif is_left_button:
            return self.__commands['left_button']
        elif has_blue_in_frame:
            return self.__commands['stop_execution']
        elif has_green_in_frame:
            self.__mouse_position = position
            return self.__commands['cursor_follow_color']

    def __identify_color(self, frame, frame_hsv, color_hsv) -> Tuple[bool, tuple]:
        mask = cv2.inRange(frame_hsv, *color_hsv)
        _, border = cv2.threshold(
            cv2.cvtColor(
                cv2.bitwise_and(frame, frame, mask=mask),
                cv2.COLOR_BGR2GRAY
            ),
            3,
            255,
            cv2.THRESH_BINARY
        )
        contours, _ = cv2.findContours(
            border,
            cv2.RETR_LIST,
            cv2.CHAIN_APPROX_SIMPLE
        )

        found_color = False
        color_position = ()
        for contour in contours:
            area = cv2.contourArea(contour)
            x, y, width, height = cv2.boundingRect(contour)
            if area > 500:
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + width, y + height),
                    (0, 0, 0),
                    4
                )
                found_color = True
                color_position = x, y
        return found_color, color_position

    def __cursor_follow_color_command(self) -> None:
        color_x_position, color_y_position = self.__mouse_position
        if pyautogui.onScreen(color_x_position, color_y_position):
            pyautogui.moveTo(color_x_position, color_y_position)

    def __left_button_command(self) -> None:
        pyautogui.click(button=pyautogui.LEFT)

    def __right_button_command(self) -> None:
        pyautogui.click(button=pyautogui.RIGHT)

    def __double_click_command(self) -> None:
        pyautogui.doubleClick()

    def __stop_execution_command(self) -> None:
        cv2.destroyAllWindows()


if __name__ == '__main__':
    MouseMove(2).run()
