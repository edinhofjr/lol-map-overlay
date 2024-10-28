import sys
from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import QTimer, QRect
from PySide6.QtGui import QPixmap
from pyautogui import keyUp
from pynput import mouse, keyboard


class ScreenCaptureWidget(QLabel):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)
        self.setGeometry(640, 540, 600, 400)

        # Timer para atualizar a captura
        self.capture_timer = QTimer()
        self.capture_timer.timeout.connect(self.update_capture)
        self.capture_timer.start(1)

        # Região da tela para capturar
        self.capture_region = QRect(400, 400, 400, 400)
        self.window_pos = QRect(400, 400, 400, 400)
        self.screen = QApplication.primaryScreen()

    def setPosition(self):
        input_coords = []

        def on_click(x, y, button, pressed):
            print('{0} at {1}'.format('Pressed' if pressed else 'Released', (x, y)))
            input_coords.append((x, y))

            if len(input_coords) == 2:
                self.window_pos = QRect(input_coords[0][0], input_coords[0][1],
                                        input_coords[1][0] - input_coords[0][0],
                                        input_coords[1][1] - input_coords[0][1])
                print(f"Região configurada: {self.window_pos}")
                self.move(self.window_pos.x(), self.window_pos.y())
                # Para o listener
                return False

            if not pressed:
                return False

        with mouse.Listener(on_click=on_click) as listener:
            listener.join()

        input_coords.clear()

    def setRegion(self):
        input_coords = []

        # Listener para capturar cliques do mouse
        def on_click(x, y, button, pressed):
            print('{0} at {1}'.format('Pressed' if pressed else 'Released', (x, y)))
            input_coords.append((x, y))

            if len(input_coords) == 2:
                # Define a nova região da captura
                self.capture_region = QRect(input_coords[0][0], input_coords[0][1],
                                            input_coords[1][0] - input_coords[0][0],
                                            input_coords[1][1] - input_coords[0][1])
                print(f"Região configurada: {self.capture_region}")
                # Para o listener
                return False

            if not pressed:  # Para o listener quando o botão é solto
                return False

        with mouse.Listener(on_click=on_click) as listener:
            listener.start()

        input_coords.clear()

    def update_capture(self):
        if self.screen:
            screenshot = self.screen.grabWindow(0, self.capture_region.x(), self.capture_region.y(),
                                                self.capture_region.width(), self.capture_region.height())
            scaled_pixmap = screenshot.scaled(self.window_pos.width(), self.window_pos.height(),
                                              QtCore.Qt.IgnoreAspectRatio,
                                              QtCore.Qt.SmoothTransformation)
            self.setPixmap(scaled_pixmap)
            self.adjustSize()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Captura de Tela")
        self.screen_capture = ScreenCaptureWidget()
        self.screen_capture.hide()

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start)
        layout.addWidget(self.start_button)

        self.position_button = QPushButton('Configure Window Position')
        self.position_button.clicked.connect(self.screen_capture.setPosition)
        layout.addWidget(self.position_button)

        self.region_button = QPushButton('Configure Screen Capture Area')
        self.region_button.clicked.connect(self.screen_capture.setRegion)
        layout.addWidget(self.region_button)

    def start(self):
        self.screen_capture.show()
        self.start_keyboard_listener()

    def start_keyboard_listener(self):
        def on_press(key):
            try:
                if key.char == "m" or key.char == "M":
                    if self.screen_capture.isVisible():
                        self.screen_capture.hide()
                    else:
                        self.screen_capture.show()
            except AttributeError:
                return

        listener = keyboard.Listener(on_press=on_press)
        listener.start()  # Inicia o listener em segundo plano

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
