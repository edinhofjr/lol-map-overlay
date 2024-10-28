import sys
from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import QTimer, QRect
from PySide6.QtGui import QPixmap

from pynput import mouse


class ScreenCaptureWidget(QLabel):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)
        self.setGeometry(100, 100, 600, 400)

        # Timer para atualizar a captura
        self.capture_timer = QTimer()
        self.capture_timer.timeout.connect(self.update_capture)
        self.capture_timer.start(1)

        # Região da tela para capturar
        self.capture_region = QRect(400, 400, 400, 400)
        self.window_pos = QRect(400, 400, 400, 400)
        self.window_x = 400
        self.window_y = 400
        self.window_h = 400
        self.window_w = 400
        self.screen = QApplication.primaryScreen()

    def setPosition(self):
        input_coords = []

        # Listener para capturar cliques do mouse
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

        # Inicia o listener de mouse
        with mouse.Listener(on_click=on_click) as listener:
            listener.join()

        # Limpar input após a captura da região
        input_coords.clear()

    def update_capture(self):
        if self.screen:
            screenshot = self.screen.grabWindow(0, self.capture_region.x(), self.capture_region.y(),
                                                self.capture_region.width(), self.capture_region.height())
            scaled_pixmap = screenshot.scaled(self.window_pos.width(), self.window_pos.height(),
                                              QtCore.Qt.IgnoreAspectRatio,
                                              QtCore.Qt.SmoothTransformation)
            #self.setPixmap(QPixmap(screenshot))
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

        self.config_button = QPushButton('Configure Window Position')
        self.config_button.clicked.connect(self.screen_capture.setPosition)
        layout.addWidget(self.config_button)

        self.config_button = QPushButton('Configure Screen Capture Area')
        self.config_button.clicked.connect(self.screen_capture.setRegion)
        layout.addWidget(self.config_button)

    def start(self):
        self.screen_capture.show()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()