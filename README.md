# Map Customizer - Twórz Własne Mapy!

## Co to jest?

`Map Customizer` to proste narzędzie, które pozwala Ci tworzyć własne, spersonalizowane mapy! Możesz na nich dodawać nazwy dzielnic i zaznaczać miejsca fotoradarów, a także zmieniać ich wygląd, kolory i przezroczystość. Na koniec możesz zapisać swoją nową mapę jako obrazek.

## Co potrzebujesz, żeby zacząć?

Wystarczy, że masz zainstalowany program **Python w wersji 3.8 lub nowszej** na swoim komputerze. To tak jak z innymi programami, które instalujesz.

## Jak to zainstalować i uruchomić?

Postępuj zgodnie z tymi prostymi krokami:

### Krok 1: Zainstaluj Pythona (jeśli jeszcze go nie masz)

**Najłatwiejszy sposób (dla Windows):**

1. Otwórz **Microsoft Store** na swoim komputerze.

2. Wyszukaj "Python" (np. "Python 3.10" lub najnowsza stabilna wersja).

3. Kliknij "Zainstaluj" lub "Pobierz".

   * **Ważne:** Python z Microsoft Store automatycznie doda się do "ścieżki" (PATH), więc nie musisz się tym martwić!

**Alternatywny sposób (dla Windows, macOS, Linux):**

* Pobierz instalator Pythona ze strony: [https://www.python.org/downloads/](https://www.python.org/downloads/)

* **Ważne (tylko przy instalacji z python.org):** Podczas instalacji Pythona **koniecznie zaznacz opcję "Add Python to PATH"** (lub "Dodaj Pythona do zmiennych środowiskowych"), jeśli taka się pojawi. To bardzo ważne, żeby programy działały poprawnie.

### Krok 2: Przygotuj pliki programu

1. **Pobierz program:**

   * Przejdź na stronę projektu na GitHubie (np. `https://github.com/TwojaNazwaUzytkownika/NazwaRepozytorium`).

   * Kliknij zielony przycisk **"Code"** (Kod), a następnie wybierz **"Download ZIP"** (Pobierz ZIP).

   * Rozpakuj pobrany plik ZIP do dowolnego folderu na swoim komputerze (np. na Pulpit).

2. **Otwórz terminal/wiersz poleceń:**

   * **Windows:** W folderze, gdzie masz rozpakowane pliki programu, kliknij prawym przyciskiem myszy na pustym miejscu, trzymając klawisz `Shift`. Wybierz opcję "Otwórz okno programu PowerShell tutaj" lub "Otwórz wiersz poleceń tutaj".

   * **macOS/Linux:** Otwórz aplikację "Terminal" i użyj komendy `cd` (change directory), aby przejść do folderu z programem, np.: `cd ~/Pulpit/MapCustomizer`

### Krok 3: Zainstaluj potrzebne dodatki (biblioteki)

Twój program potrzebuje kilku "dodatków" (nazywamy je bibliotekami), żeby działać. Zainstalujesz je jedną komandą:

W otwartym terminalu/wierszu poleceń wpisz:

```bash
pip install -r requirements.txt
```

Naciśnij `Enter`. Poczekaj, aż instalacja się zakończy. Powinien pojawić się komunikat o sukcesie.

**Co to instaluje?**
Program potrzebuje:

* `PyQt6`: Do tworzenia okienek i przycisków.

* `Pillow`: Do pracy z obrazkami map.

### Krok 4: Uruchom program!

Gdy wszystko jest zainstalowane, możesz włączyć `Map Customizer`:

W tym samym terminalu/wierszu poleceń wpisz:

```bash
python main.py
```

Naciśnij `Enter`. Powinno pojawić się okno programu!

## Jak używać programu?

1. **Wybierz mapę:** Kliknij przycisk "Wybierz mapę" i znajdź plik obrazka mapy na swoim komputerze (np. PNG, JPG).

2. **Dostosuj warstwy:**

   * **Dzielnice:** W sekcji "Ustawienia nazw dzielnic" możesz zmieniać czcionkę, rozmiar tekstu, jak długie mają być nazwy, oraz kolory tekstu i jego obwódki.

   * **Fotoradary:** W sekcji "Ustawienia fotoradarów" możesz ustawić, jak duży ma być przezroczysty obszar wokół fotoradaru, jego kolor, kolor samej ikonki fotoradaru. Możesz też zdecydować, czy chcesz, żeby pokazywała się prędkość, i dostosować jej wygląd.

3. **Wygeneruj nową mapę:** Kliknij "Wygeneruj mapę". Program stworzy nową mapę z Twoimi zmianami i zapisze ją w folderze `output/` (w tym samym miejscu, gdzie masz pliki programu). Każda nowa mapa będzie miała unikalną nazwę z datą i godziną, więc nie nadpiszesz starych!

## Struktura plików (dla ciekawskich)

* `main.py`: To główny plik, który uruchamia program.

* `sections/`: Tutaj są "sekcje" programu, czyli osobne części do obsługi dzielnic (`districts.py`) i fotoradarów (`speed_cameras.py`).

* `resources/`: W tym folderze są obrazki (np. domyślna mapa `map.png`, ikonka `radar.png`) i czcionki. Tutaj też powinny być pliki z danymi fotoradarów (`speed_cameras.json`).

## Licencja

Ten program jest darmowy i możesz z nim robić, co chcesz (licencja MIT).