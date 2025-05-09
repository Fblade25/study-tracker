# src/styles/style.py

from .colors import Colors


def apply_style(app):
    style_sheet = f"""
        QWidget {{
            background-color: {Colors.BACKGROUND};
            color: {Colors.TEXT};
            font-family: Arial, sans-serif;
            font-size: 14px;
        }}
        
        QPushButton {{
            background-color: {Colors.PRIMARY};
            color: {Colors.TEXT};
            border-radius: 0px;
            padding: 5px;
            margin-bottom: 10px;
            border: 1px solid {Colors.BORDER_COLOR};
        }}
        
        QPushButton:hover {{
            background-color: {Colors.BUTTON_HOVER};
        }}
        
        QPushButton:pressed {{
            background-color: {Colors.BUTTON_ACTIVE};
        }}
        
        QLabel {{
            color: {Colors.TEXT};
        }}
        
        QLineEdit {{
            background-color: #333;
            color: {Colors.TEXT};
            border: 1px solid {Colors.BORDER_COLOR};
            padding: 5px;
        }}
        
        QComboBox {{
            background-color: #333;
            color: {Colors.TEXT};
            border: 1px solid {Colors.BORDER_COLOR};
        }}
        
        QTabWidget::pane {{
            border: 1px solid {Colors.BORDER_COLOR};
            background-color: {Colors.BACKGROUND};
        }}
        
        QTabBar::tab {{
            background-color: {Colors.SECONDARY};
            color: {Colors.TEXT};
            padding: 5px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {Colors.PRIMARY};
        }}
        
        QDockWidget::title {{
            background-color: {Colors.ACCENT};
            color: {Colors.TEXT};
        }}
        
        QScrollBar {{
            background-color: #444;
            border-radius: 5px;
        }}
        
        QScrollBar::handle {{
            background-color: {Colors.PRIMARY};
            border-radius: 5px;
        }}
        
        QScrollBar::handle:hover {{
            background-color: {Colors.BUTTON_HOVER};
        }}
    """
    app.setStyleSheet(style_sheet)
