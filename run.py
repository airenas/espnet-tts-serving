import os
import sys

import uvicorn
from service.service import create_service

from fastapi.logger import logger
import logging

ll = os.environ.get('LOG_LEVEL', 'INFO').upper()
logger.setLevel(level=ll)
if __name__ != "__main__":
    logger.handlers = [logging.StreamHandler(sys.stdout)]
    # unicorn_logger = logging.getLogger('unicorn')
    # logger.setLevel(unicorn_logger.level)

logger.info("Starting espnet-tts-serving service")
app = create_service()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
