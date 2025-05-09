import sys

from components.main_window import MainWindow
from PySide6.QtWidgets import QApplication
from styles.style import apply_style


def main():
    app = QApplication(sys.argv)

    # Apply the global styles
    apply_style(app)

    # Initialize and show the main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
