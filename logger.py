from __future__ import annotations

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(module)s.py %(funcName)s %(message)s",
)
logger = logging.getLogger(__name__)
