import os
import sys

import uvicorn
from service.service import create_service

from fastapi.logger import logger
import logging

ll = os.environ.get('LOG_LEVEL', 'INFO').upper()
logger.setLevel(level=ll)
logger.handlers = [logging.StreamHandler(sys.stdout)]

logger.info("Starting espnet-tts-serving service")
app = create_service()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info("Using port: %d" % port)
    uvicorn.run(app, host="0.0.0.0", port=port)
