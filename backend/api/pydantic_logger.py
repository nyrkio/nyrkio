import logging
import os

# Disable uvicorn access logger
uvicorn_access = logging.getLogger("uvicorn.access")
uvicorn_access.disabled = True

logger = logging.getLogger("uvicorn")

if os.environ.get("DEBUG", False) or os.environ.get("NYRKIO_DEBUG", False):
    logger.setLevel(logging.getLevelName(logging.DEBUG))
else:
    logger.setLevel(logging.getLevelName(logging.INFO))
