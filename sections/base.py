from PyQt6.QtWidgets import QWidget

class Section:
    def get_name(self) -> str:
        raise NotImplementedError

    def get_widget(self) -> QWidget:
        raise NotImplementedError

    def is_enabled(self) -> bool:
        raise NotImplementedError

    def render(self, image, draw):
        raise NotImplementedError