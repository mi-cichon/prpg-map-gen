import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QLineEdit, QMessageBox, QInputDialog, QScrollArea
)
from PyQt6.QtGui import QPixmap, QImage, QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QPoint, pyqtSignal # Import pyqtSignal

from PIL import Image, ImageDraw, ImageFont # For drawing on the image
from PIL.ImageQt import ImageQt # For converting PIL Image to QImage/QPixmap

class ClickableImageLabel(QLabel):
    """
    Niestandardowa klasa QLabel, która emituje sygnał z współrzędnymi kliknięcia myszy
    w odniesieniu do oryginalnego rozmiaru obrazu, nawet jeśli obraz jest skalowany.
    """
    # Sygnał emitujący współrzędne x, y kliknięcia
    clicked = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        # Włącz śledzenie myszy, aby wykrywać kliknięcia
        self.setMouseTracking(True)
        # Skaluj zawartość obrazu, aby dopasować ją do rozmiaru etykiety
        self.setScaledContents(True)

    def mousePressEvent(self, event):
        """
        Obsługuje zdarzenia kliknięcia myszy na etykiecie.
        Konwertuje pozycję kliknięcia QLabel na współrzędne oryginalnego obrazu.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # Pobierz pozycję kliknięcia względem QLabel
            pos = event.pos()
            pixmap = self.pixmap()

            if pixmap and not pixmap.isNull():
                # Pobierz wymiary oryginalnego pixmapy
                pm_width = pixmap.width()
                pm_height = pixmap.height()
                # Pobierz wymiary aktualnej etykiety QLabel
                label_width = self.width()
                label_height = self.height()

                # Oblicz współczynniki skalowania
                scale_x = pm_width / label_width
                scale_y = pm_height / label_height

                # Zastosuj skalowanie, aby uzyskać współrzędne oryginalnego pixmapy
                original_x = int(pos.x() * scale_x)
                original_y = int(pos.y() * scale_y)

                # Emituj sygnał z oryginalnymi współrzędnymi
                self.clicked.emit(original_x, original_y)
        super().mousePressEvent(event)

class MapClickExtractorApp(QWidget):
    """
    Główna aplikacja do ekstrakcji lokalizacji z mapy.
    Umożliwia ładowanie mapy, klikanie na nią w celu dodawania punktów
    (z nazwą i prędkością) oraz zapisywanie tych punktów do pliku JSON.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Narzędzie do Ekstrakcji Lokalizacji z Mapy")
        self.setGeometry(100, 100, 1000, 700) # Ustaw większy rozmiar okna

        self.map_path = None
        self.original_image = None # Obraz PIL (do rysowania)
        self.current_display_pixmap = None # QPixmap (do wyświetlania)
        self.points_data = [] # Lista do przechowywania danych punktów {"name": "...", "x": ..., "y": ..., "speed": "..."}

        self.setup_ui()

    def setup_ui(self):
        """Inicjalizuje interfejs użytkownika aplikacji."""
        main_layout = QVBoxLayout()
        control_layout = QHBoxLayout()

        # Obszar wyświetlania obrazu
        self.image_label = ClickableImageLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Połącz sygnał kliknięcia z metodą obsługi
        self.image_label.clicked.connect(self.handle_image_click)

        # Obszar przewijania dla obrazu (ważne dla dużych map)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.image_label)
        main_layout.addWidget(scroll_area)

        # Przyciski i pola kontrolne
        self.load_map_btn = QPushButton("Wybierz mapę")
        self.load_map_btn.clicked.connect(self.load_map)
        control_layout.addWidget(self.load_map_btn)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Wprowadź nazwę (np. Fotoradar 1)")
        control_layout.addWidget(self.name_input)

        self.x_display = QLabel("X: -")
        self.y_display = QLabel("Y: -")
        control_layout.addWidget(self.x_display)
        control_layout.addWidget(self.y_display)

        self.add_point_btn = QPushButton("Dodaj Punkt")
        self.add_point_btn.clicked.connect(self.add_point)
        self.add_point_btn.setEnabled(False) # Wyłącz na początku, dopóki mapa nie zostanie załadowana
        control_layout.addWidget(self.add_point_btn)

        self.undo_btn = QPushButton("Cofnij Ostatni")
        self.undo_btn.clicked.connect(self.undo_last_point)
        self.undo_btn.setEnabled(False) # Wyłącz na początku
        control_layout.addWidget(self.undo_btn)

        self.save_btn = QPushButton("Zapisz do JSON")
        self.save_btn.clicked.connect(self.save_to_json)
        self.save_btn.setEnabled(False) # Wyłącz na początku
        control_layout.addWidget(self.save_btn)

        self.clear_btn = QPushButton("Wyczyść Wszystko")
        self.clear_btn.clicked.connect(self.clear_all_points)
        self.clear_btn.setEnabled(False) # Wyłącz na początku
        control_layout.addWidget(self.clear_btn)

        main_layout.addLayout(control_layout)
        self.setLayout(main_layout)

    def load_map(self):
        """Otwiera okno dialogowe wyboru pliku i ładuje wybraną mapę."""
        path, _ = QFileDialog.getOpenFileName(self, "Wybierz mapę", "", "Obrazy (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self.map_path = path
            try:
                # Otwórz obraz PIL i przekonwertuj na RGBA dla spójności
                self.original_image = Image.open(self.map_path).convert("RGBA")
                self.update_map_display() # Wyświetl mapę
                # Włącz odpowiednie przyciski
                self.add_point_btn.setEnabled(True)
                self.save_btn.setEnabled(True)
                self.clear_btn.setEnabled(True)
                self.undo_btn.setEnabled(False) # Resetuj stan przycisku cofania
                self.points_data = [] # Wyczyść poprzednie punkty przy ładowaniu nowej mapy
                QMessageBox.information(self, "Mapa załadowana", f"Mapa '{os.path.basename(path)}' załadowana pomyślnie.")
            except Exception as e:
                QMessageBox.critical(self, "Błąd ładowania mapy", f"Nie udało się załadować mapy: {e}")
                # Zresetuj stan aplikacji w przypadku błędu
                self.map_path = None
                self.original_image = None
                self.image_label.clear()
                self.add_point_btn.setEnabled(False)
                self.save_btn.setEnabled(False)
                self.clear_btn.setEnabled(False)
                self.undo_btn.setEnabled(False)

    def handle_image_click(self, x, y):
        """
        Obsługuje kliknięcie na obrazie, wyświetlając współrzędne
        i przygotowując do dodania punktu.
        """
        self.x_display.setText(f"X: {x}")
        self.y_display.setText(f"Y: {y}")
        self.current_clicked_x = x
        self.current_clicked_y = y
        # Opcjonalnie, ustaw focus na polu nazwy
        self.name_input.setFocus()

    def add_point(self):
        """
        Dodaje nowy punkt do listy na podstawie klikniętych współrzędnych
        i wprowadzonych danych.
        """
        if not self.original_image:
            QMessageBox.warning(self, "Brak mapy", "Najpierw załaduj mapę.")
            return

        # Sprawdź, czy użytkownik kliknął na mapę
        if not hasattr(self, 'current_clicked_x') or not hasattr(self, 'current_clicked_y'):
            QMessageBox.warning(self, "Brak kliknięcia", "Kliknij na mapę, aby wybrać lokalizację.")
            return

        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Brak nazwy", "Wprowadź nazwę dla punktu.")
            return

        # Użyj QInputDialog do pobrania prędkości
        speed_text, ok = QInputDialog.getText(self, "Wprowadź Prędkość", f"Wprowadź prędkość dla '{name}' (np. 50 km/h):")
        if not ok or not speed_text.strip():
            QMessageBox.warning(self, "Brak prędkości", "Prędkość jest wymagana.")
            return

        # Stwórz słownik z danymi punktu
        point = {
            "name": name,
            "x": self.current_clicked_x,
            "y": self.current_clicked_y,
            "speed": speed_text.strip()
        }
        self.points_data.append(point) # Dodaj punkt do listy
        self.update_map_display() # Odśwież wyświetlanie mapy z nowym punktem
        self.name_input.clear() # Wyczyść pole nazwy
        self.x_display.setText("X: -") # Zresetuj wyświetlanie współrzędnych
        self.y_display.setText("Y: -")
        # Usuń tymczasowe atrybuty kliknięcia
        del self.current_clicked_x
        del self.current_clicked_y
        self.undo_btn.setEnabled(True) # Włącz przycisk cofania
        QMessageBox.information(self, "Punkt dodany", f"Dodano punkt: {name} ({point['x']}, {point['y']})")


    def undo_last_point(self):
        """Usuwa ostatnio dodany punkt z listy."""
        if self.points_data:
            removed_point = self.points_data.pop()
            self.update_map_display() # Odśwież wyświetlanie mapy
            if not self.points_data:
                self.undo_btn.setEnabled(False) # Wyłącz przycisk cofania, jeśli nie ma punktów
            QMessageBox.information(self, "Cofnięto", f"Usunięto ostatni punkt: {removed_point['name']}")
        else:
            QMessageBox.warning(self, "Brak punktów", "Brak punktów do cofnięcia.")
            self.undo_btn.setEnabled(False)

    def save_to_json(self):
        """Zapisuje wszystkie zebrane punkty do pliku JSON."""
        if not self.points_data:
            QMessageBox.warning(self, "Brak danych", "Brak punktów do zapisania.")
            return

        # Otwórz okno dialogowe zapisu pliku
        file_path, _ = QFileDialog.getSaveFileName(self, "Zapisz punkty jako JSON", "speed_cameras.json", "Pliki JSON (*.json)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    # Zapisz dane do JSON z wcięciami dla czytelności i obsługą polskich znaków
                    json.dump(self.points_data, f, indent=4, ensure_ascii=False)
                QMessageBox.information(self, "Zapisano", f"Punkty zapisano pomyślnie do: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Błąd zapisu", f"Nie udało się zapisać pliku JSON: {e}")

    def clear_all_points(self):
        """Czyści wszystkie zebrane punkty po potwierdzeniu przez użytkownika."""
        if QMessageBox.question(self, "Potwierdź czyszczenie", "Czy na pewno chcesz wyczyścić wszystkie punkty?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.points_data = [] # Wyczyść listę punktów
            self.update_map_display() # Odśwież wyświetlanie mapy
            self.undo_btn.setEnabled(False) # Wyłącz przycisk cofania
            QMessageBox.information(self, "Wyczyszczono", "Wszystkie punkty zostały wyczyszczone.")

    def update_map_display(self):
        """
        Odświeża wyświetlanie mapy, rysując na niej wszystkie dodane punkty
        i ich nazwy.
        """
        if self.original_image:
            # Utwórz kopię oryginalnego obrazu do rysowania
            display_image = self.original_image.copy()
            draw = ImageDraw.Draw(display_image)

            # Zdefiniuj czcionkę do rysowania tekstu na mapie
            try:
                # Spróbuj załadować czcionkę Fredoka-Bold.ttf, jeśli istnieje
                font_path = "resources/Fredoka-Bold.ttf"
                if not os.path.exists(font_path):
                    # Fallback do domyślnej czcionki PIL, jeśli plik czcionki nie istnieje
                    font = ImageFont.load_default()
                else:
                    font = ImageFont.truetype(font_path, 16)
            except Exception:
                # W przypadku błędu ładowania czcionki, użyj domyślnej
                font = ImageFont.load_default()

            for point in self.points_data:
                x, y = point["x"], point["y"]
                name = point["name"]
                speed = point.get("speed", "") # Pobierz prędkość, domyślnie pusty string jeśli brak

                # Rysuj kółko symbolizujące punkt
                radius = 5
                draw.ellipse((x - radius, y - radius, x + radius, y + radius),
                             fill=(255, 0, 0, 180), # Czerwony, półprzezroczysty
                             outline=(255, 255, 255, 255)) # Biała obwódka

                # Rysuj tekst (nazwa i prędkość)
                text_to_draw = f"{name}\n({speed})"
                # Oblicz rozmiar tekstu dla centrowania
                bbox = draw.textbbox((0,0), text_to_draw, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                text_x = x - text_width / 2
                text_y = y + radius + 2 # Przesunięcie poniżej kółka

                # Rysuj tekst z obwódką (dla lepszej czytelności)
                outline_width = 1
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        if dx != 0 or dy != 0:
                            draw.text((text_x + dx, text_y + dy), text_to_draw, font=font, fill=(0, 0, 0, 255)) # Czarna obwódka
                draw.text((text_x, text_y), text_to_draw, font=font, fill=(255, 255, 0, 255)) # Żółty tekst

            # Konwertuj obraz PIL na QPixmap do wyświetlenia w QLabel
            qimage = ImageQt(display_image)
            self.current_display_pixmap = QPixmap.fromImage(qimage)
            self.image_label.setPixmap(self.current_display_pixmap)
        else:
            self.image_label.clear() # Wyczyść etykietę, jeśli nie ma obrazu


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapClickExtractorApp()
    window.show()
    sys.exit(app.exec())
