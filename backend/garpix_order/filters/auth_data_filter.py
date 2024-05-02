import re
import logging


class AuthDataFilter(logging.Filter):
    pattern = re.compile(r"&?(userName|password|token)=[^&]*")

    def filter(self, record):
        record.msg = self.mask_auth_data(record.msg)
        return True

    def mask_auth_data(self, message):
        message = self.pattern.sub("auth_data=*****", message)
        return message
