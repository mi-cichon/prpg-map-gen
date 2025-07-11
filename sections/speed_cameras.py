import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QLineEdit, QMessageBox, QInputDialog, QScrollArea, QGroupBox, QSpinBox, QColorDialog, QCheckBox
)
from PyQt6.QtGui import QPixmap, QImage, QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QPoint, pyqtSignal 

from PIL import Image, ImageDraw, ImageFont 
from PIL.ImageQt import ImageQt 

try:
    from .base import Section
except ImportError:
    
    class Section:
        def get_name(self) -> str:
            raise NotImplementedError
        def get_widget(self) -> QWidget:
            raise NotImplementedError
        def is_enabled(self) -> bool:
            raise NotImplementedError
        def render(self, image, draw):
            raise NotImplementedError

class SpeedCamerasSection(Section):
    def __init__(self):
        self.enabled_checkbox = QCheckBox("Generuj fotoradary")
        self.enabled_checkbox.setChecked(True)

        self.circle_radius_spinner = QSpinBox()
        self.circle_radius_spinner.setRange(10, 100) 
        self.circle_radius_spinner.setValue(60) 

        self.circle_color = QColor(255, 0, 0, 50)
        self.circle_color_btn = QPushButton("Kolor obszaru kółka")
        self.circle_color_btn.clicked.connect(self.choose_circle_color)

        self.icon_color = QColor(254, 127, 0, 255)
        self.icon_color_btn = QPushButton("Kolor ikonki")
        self.icon_color_btn.clicked.connect(self.choose_icon_color)

        self.show_speed_checkbox = QCheckBox("Pokaż prędkość")
        self.show_speed_checkbox.setChecked(True) 

        self.font_input = QLineEdit("resources/Fredoka-Bold.ttf")
        self.font_size_spinner = QSpinBox()
        self.font_size_spinner.setRange(6, 100)
        self.font_size_spinner.setValue(14)

        self.text_color = QColor(254, 127, 0) 
        self.text_outline_color = QColor(0, 0, 0) 
        self.text_color_btn = QPushButton("Kolor tekstu prędkości")
        self.text_color_btn.clicked.connect(self.choose_text_color)
        self.text_outline_color_btn = QPushButton("Kolor obramowania tekstu prędkości")
        self.text_outline_color_btn.clicked.connect(self.choose_text_outline_color)
        self.text_outline_width_spinner = QSpinBox()
        self.text_outline_width_spinner.setRange(0, 5)
        self.text_outline_width_spinner.setValue(1)

        self.widget = QGroupBox("Ustawienia fotoradarów")
        layout = QVBoxLayout()
        layout.addWidget(self.enabled_checkbox)
        layout.addWidget(QLabel("Promień obszaru kółka:"))
        layout.addWidget(self.circle_radius_spinner)
        layout.addWidget(self.circle_color_btn)
        layout.addWidget(self.icon_color_btn)
        layout.addWidget(self.show_speed_checkbox) 
        layout.addWidget(QLabel("Czcionka tekstu prędkości:"))
        layout.addWidget(self.font_input)
        layout.addWidget(QLabel("Rozmiar czcionki tekstu prędkości:"))
        layout.addWidget(self.font_size_spinner)
        layout.addWidget(self.text_color_btn)
        layout.addWidget(self.text_outline_color_btn)
        layout.addWidget(QLabel("Grubość obramowania tekstu prędkości:"))
        layout.addWidget(self.text_outline_width_spinner)
        self.widget.setLayout(layout)

    def get_name(self):
        return "speed_cameras"

    def get_widget(self):
        return self.widget

    def is_enabled(self):
        return self.enabled_checkbox.isChecked()

    def choose_circle_color(self):
        color = QColorDialog.getColor(self.circle_color)
        if color.isValid():
            self.circle_color = color

    def choose_icon_color(self):
        color = QColorDialog.getColor(self.icon_color)
        if color.isValid():
            self.icon_color = color

    def choose_text_color(self):
        color = QColorDialog.getColor(self.text_color)
        if color.isValid():
            self.text_color = color

    def choose_text_outline_color(self):
        color = QColorDialog.getColor(self.text_outline_color)
        if color.isValid():
            self.text_outline_color = color

    def render(self, image, draw):
        try:
            import json
            
            json_path = "resources/speed_cameras.json"
            if not os.path.exists(json_path):
                print(f"[SpeedCamerasSection] Błąd: Plik '{json_path}' nie istnieje. Nie można wyrenderować fotoradarów.")
                return

            with open(json_path, "r", encoding="utf-8") as f:
                speed_cameras_data = json.load(f)

            circle_radius = self.circle_radius_spinner.value()
            
            circle_fill_color = self.circle_color.getRgb()

            icon_path = "resources/radar.png"
            radar_icon = None
            if os.path.exists(icon_path):
                radar_icon = Image.open(icon_path).convert("RGBA")
                
                icon_size = int(circle_radius * 0.5) 
                if icon_size < 10: icon_size = 10 
                radar_icon = radar_icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)

                icon_tint_color = self.icon_color.getRgb()
                
                colored_icon = Image.new("RGBA", radar_icon.size, icon_tint_color)
                
                radar_icon_data = radar_icon.getdata()
                new_icon_data = []
                for item in radar_icon_data:
                    
                    new_icon_data.append((icon_tint_color[0], icon_tint_color[1], icon_tint_color[2], item[3]))
                colored_icon.putdata(new_icon_data)
                radar_icon = colored_icon
            else:
                print(f"[SpeedCamerasSection] Ostrzeżenie: Plik ikonki '{icon_path}' nie istnieje. Fotoradary będą renderowane bez ikon.")

            font_path = self.font_input.text()
            font_size = self.font_size_spinner.value()
            try:
                if not os.path.exists(font_path):
                    font = ImageFont.load_default()
                else:
                    font = ImageFont.truetype(font_path, font_size)
            except Exception:
                font = ImageFont.load_default()

            text_fill_color = self.text_color.getRgb()[:3]
            text_outline_color = self.text_outline_color.getRgb()[:3]
            text_outline_width = self.text_outline_width_spinner.value()
            show_speed = self.show_speed_checkbox.isChecked()

            for camera in speed_cameras_data:
                name = camera["name"] 
                x, y = camera["x"], camera["y"]
                speed = camera.get("speed", "") 
                
                temp_circle_image = Image.new("RGBA", image.size, (0,0,0,0))
                temp_draw = ImageDraw.Draw(temp_circle_image)
                temp_draw.ellipse((x - circle_radius, y - circle_radius, x + circle_radius, y + circle_radius),
                                  fill=circle_fill_color) 
                image.alpha_composite(temp_circle_image)

                if radar_icon:
                    icon_x = x - radar_icon.width // 2
                    icon_y = y - radar_icon.height // 2

                    image.paste(radar_icon, (icon_x, icon_y), radar_icon)

                
                if show_speed and speed:
                    text_to_draw = speed
                    
                    bbox = draw.textbbox((0,0), text_to_draw, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]

                    text_y_start = y + icon_size / 2 
                    text_y = text_y_start - text_height + 10 
                    
                    text_x = x - text_width / 2

                    for dx in range(-text_outline_width, text_outline_width + 1):
                        for dy in range(-text_outline_width, text_outline_width + 1):
                            if dx != 0 or dy != 0:
                                draw.text((text_x + dx, text_y + dy), text_to_draw, font=font, fill=text_outline_color)
                    draw.text((text_x, text_y), text_to_draw, font=font, fill=text_fill_color)

        except Exception as e:
            print(f"[SpeedCamerasSection] Błąd renderowania: {e}")
