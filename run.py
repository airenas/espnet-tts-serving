import logging
import os
import sys

import uvicorn
from fastapi.logger import logger
from uvicorn.config import LOGGING_CONFIG

from service.service import create_service

ll = os.environ.get('LOG_LEVEL', 'INFO').upper()
logger.setLevel(level=ll)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("[%(asctime)s.%(msecs)03d] %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)
LOGGING_CONFIG["formatters"]["default"]["fmt"] = "[%(asctime)s.%(msecs)03d] %(levelname)s - %(message)s"
LOGGING_CONFIG["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"

logger.info("Starting espnet-tts-serving service")
app = create_service()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info("Using port: %d" % port)
    uvicorn.run(app, host="0.0.0.0", port=port)
