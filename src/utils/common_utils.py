import random
import string
from uuid import uuid4
from src.utils.logging_utils import setup_logging

logger = setup_logging(__name__)

def generate_credential_id() -> str:
    prefix = random.choice(string.ascii_lowercase)
    raw_uuid = str(uuid4()).replace("-", "")
    credential_id = f"{prefix}{raw_uuid}"
    logger.info("Generated credential ID: %s", credential_id)
    return credential_id
