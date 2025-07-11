import sys
import os
from PIL import Image, ImageDraw
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QMessageBox
)
from sections.districts import DistrictsSection
from sections.speed_cameras import SpeedCamerasSection
import datetime

class MapCustomizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Map Customizer")
        self.resize(400, 500)

        self.map_path = "resources/map.png"
        self.sections = [
            SpeedCamerasSection(),
            DistrictsSection()
        ]

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.map_btn = QPushButton("Wybierz mapę")
        self.map_btn.clicked.connect(self.choose_map)
        layout.addWidget(self.map_btn)

        for section in self.sections:
            layout.addWidget(section.get_widget())

        self.generate_btn = QPushButton("Wygeneruj mapę")
        self.generate_btn.clicked.connect(self.generate_map)
        layout.addWidget(self.generate_btn)

        self.setLayout(layout)

    def choose_map(self):
        path, _ = QFileDialog.getOpenFileName(self, "Wybierz mapę", "", "Obrazy (*.png *.jpg *.jpeg)")
        if path:
            self.map_path = path

    def generate_map(self):
        try:
            image = Image.open(self.map_path).convert("RGBA")
            draw = ImageDraw.Draw(image)

            for section in self.sections:
                if section.is_enabled():
                    section.render(image, draw)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"custom_map_{timestamp}.png")
            image.save(output_path)
            os.startfile(output_path)
            QMessageBox.information(self, "Sukces", f"Zapisano jako: {output_path}")

        except Exception as e:
            QMessageBox.critical(self, "Błąd", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapCustomizer()
    window.show()
    sys.exit(app.exec())
