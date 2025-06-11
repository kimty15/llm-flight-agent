"""
File khởi động chính cho Nha Trang Tourism Assistant API.

File này khởi động FastAPI server và cấu hình logging.
"""

import uvicorn
from src.api.main import app
from src.core.config import settings
from src.utils.logger import get_logger

def setup_logging():
    """Cấu hình logging cho ứng dụng."""
    logger = get_logger(__name__)
    logger.info("=== Nha Trang Tourism Assistant API ===")
    logger.info(f"Phiên bản: {settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Host: {settings.HOST}")
    logger.info(f"Port: {settings.PORT}")
    logger.info("Đang khởi động server...")

def main():
    """Hàm chính để khởi động ứng dụng."""
    # Cấu hình logging
    setup_logging()
    
    # Khởi động ứng dụng FastAPI
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )

if __name__ == "__main__":
    main() 