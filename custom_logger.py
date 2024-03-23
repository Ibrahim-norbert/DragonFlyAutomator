import logging
import os



# Custom logging handler to store log messages
class ListHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_messages = []

    def emit(self, record):
        # List to store log messages
        self.log_messages.append(self.format(record))



