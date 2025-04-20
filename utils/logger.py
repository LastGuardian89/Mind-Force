import logging
import json
from datetime import datetime

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )

class RequestLogger:
    def __init__(self):
        self.logger = logging.getLogger('security')

    def log(self, event_type: str, details: dict):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': event_type,
            'details': details
        }
        self.logger.info(json.dumps(log_entry))