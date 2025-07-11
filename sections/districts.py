import json
import textwrap
from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton, QColorDialog, QCheckBox
from PyQt6.QtGui import QColor, QFont
from PIL import ImageDraw, ImageFont
from .base import Section

class DistrictsSection(Section):
    def __init__(self):
        self.enabled_checkbox = QCheckBox("Generuj nazwy dzielnic")
        self.enabled_checkbox.setChecked(True)

        self.font_input = QLineEdit("resources/Fredoka-Bold.ttf")
        self.font_size_spinner = QSpinBox()
        self.font_size_spinner.setRange(6, 100)
        self.font_size_spinner.setValue(18)

        self.wrap_spinner = QSpinBox()
        self.wrap_spinner.setRange(5, 30)
        self.wrap_spinner.setValue(8)

        self.outline_spinner = QSpinBox()
        self.outline_spinner.setRange(0, 10)
        self.outline_spinner.setValue(1)

        self.text_color = QColor(255, 255, 255)
        self.outline_color = QColor(0, 0, 0)

        self.color_btn = QPushButton("Kolor tekstu")
        self.color_btn.clicked.connect(self.choose_text_color)
        self.outline_btn = QPushButton("Kolor obramowania")
        self.outline_btn.clicked.connect(self.choose_outline_color)

        self.widget = QGroupBox("Ustawienia nazw dzielnic")
        layout = QVBoxLayout()
        layout.addWidget(self.enabled_checkbox)
        layout.addWidget(QLabel("Czcionka:"))
        layout.addWidget(self.font_input)
        layout.addWidget(QLabel("Rozmiar czcionki:"))
        layout.addWidget(self.font_size_spinner)
        layout.addWidget(QLabel("Zawijanie (max znaków):"))
        layout.addWidget(self.wrap_spinner)
        layout.addWidget(QLabel("Grubość obramowania:"))
        layout.addWidget(self.outline_spinner)
        layout.addWidget(self.color_btn)
        layout.addWidget(self.outline_btn)
        self.widget.setLayout(layout)

    def get_name(self):
        return "districts"

    def get_widget(self):
        return self.widget

    def is_enabled(self):
        return self.enabled_checkbox.isChecked()

    def choose_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_color = color

    def choose_outline_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.outline_color = color

    def render(self, image, draw):
        try:
            with open("resources/districts.json", "r", encoding="utf-8") as f:
                districts = json.load(f)

            font_path = self.font_input.text()
            font_size = self.font_size_spinner.value()
            wrap_limit = self.wrap_spinner.value()
            outline_width = self.outline_spinner.value()
            line_spacing = 4

            font = ImageFont.truetype(font_path, font_size)

            for district in districts:
                name = district["name"]
                x, y = district["x"], district["y"]

                lines = textwrap.wrap(
                    name,
                    width=wrap_limit,
                    break_long_words=False,
                    break_on_hyphens=False
                )

                total_height = len(lines) * (font_size + line_spacing)
                start_y = y - total_height // 2

                for i, line in enumerate(lines):
                    text_width = font.getlength(line)
                    line_x = x - text_width / 2
                    line_y = start_y + i * (font_size + line_spacing)

                    for dx in range(-outline_width, outline_width + 1):
                        for dy in range(-outline_width, outline_width + 1):
                            if dx != 0 or dy != 0:
                                draw.text((line_x + dx, line_y + dy), line, font=font, fill=self.outline_color.getRgb()[:3])

                    draw.text((line_x, line_y), line, font=font, fill=self.text_color.getRgb()[:3])

        except Exception as e:
            print(f"[DistrictsSection] Błąd: {e}")