class AppColors:
    # Primary brand color (Cherry Red)
    PRIMARY = "#DE3163"
    # Darker shade of primary for hover effects
    PRIMARY_DARK = "#C42B56"
    # Lighter shade of primary for backgrounds
    PRIMARY_LIGHT = "#F5D6E0"
    # Secondary color for accents
    SECONDARY = "#4A90E2"
    # Text colors
    TEXT_DARK = "#333333"
    TEXT_LIGHT = "#FFFFFF"
    # Background colors
    BG_LIGHT = "#FFFFFF"
    BG_MEDIUM = "#F5F5F5"
    BG_DARK = "#E0E0E0"
    # Success, warning, error colors
    SUCCESS = "#4CAF50"
    WARNING = "#FFC107"
    ERROR = "#F44336"

def get_application_stylesheet():
    """Returns the global application stylesheet"""
    return f"""
        QMainWindow, QWidget {{
            background-color: {AppColors.BG_LIGHT};
            color: {AppColors.TEXT_DARK};
        }}
        
        QGroupBox {{
            font-weight: bold;
            border: 1px solid {AppColors.BG_DARK};
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 12px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 5px;
            color: {AppColors.PRIMARY};
        }}
        
        QPushButton {{
            background-color: {AppColors.PRIMARY};
            color: {AppColors.TEXT_LIGHT};
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            border: none;
        }}
        
        QPushButton:hover {{
            background-color: {AppColors.PRIMARY_DARK};
        }}
        
        QPushButton:pressed {{
            background-color: {AppColors.PRIMARY_DARK};
            padding: 9px 15px 7px 17px;
        }}
        
        QLineEdit {{
            padding: 6px;
            border: 1px solid {AppColors.BG_DARK};
            border-radius: 4px;
        }}
        
        QLineEdit:focus {{
            border: 1px solid {AppColors.PRIMARY};
        }}
        
        QProgressBar {{
            border: 1px solid {AppColors.BG_DARK};
            border-radius: 4px;
            text-align: center;
            height: 20px;
        }}
        
        QProgressBar::chunk {{
            background-color: {AppColors.PRIMARY};
            border-radius: 3px;
        }}
    """