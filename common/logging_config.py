"""
Конфигурация логирования для приложения.
"""
import logging

def setup_logging():
    """
    Настраивает конфигурацию логирования для приложения.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
