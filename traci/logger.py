import logging
import env

# redefine the levels so they are accessible for places that use this lib
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

was_instantiated = False

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;5;247m"
    white = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    levelname = "[{levelname}]"
    rest_of_format = " {message}"

    FORMATS = {
        logging.DEBUG: grey + levelname + "   " + reset + rest_of_format,
        logging.INFO: white + levelname + "    " + reset + rest_of_format,
        logging.WARNING: yellow + levelname + " " + reset + rest_of_format,
        logging.ERROR: red + levelname + "   " + reset + rest_of_format,
        logging.CRITICAL: bold_red + levelname + reset + rest_of_format
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, style='{')
        return formatter.format(record)

def get_logger(name, log_level=INFO, log_to_file=False, file_name="/tmp/traci.log"):
    '''returns logger with fancy formatting.
    
    file_name is only used if log_to_file is True
    '''
    global was_instantiated

    if not was_instantiated:
        if log_to_file:
            logging.basicConfig(level=DEBUG,
                format="%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)", # %(name)s
                filename=file_name,
                filemode='w')

        logger = logging.getLogger(name)
        logger.setLevel(log_level)

        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(log_level)

        ch.setFormatter(CustomFormatter())

        logger.addHandler(ch)

        was_instantiated = True

        return logger
    else:
        return logging.getLogger(name)

if __name__ == "__main__":
    logger = get_logger("logger_test")
    logger.debug('Hmm')
    logger.info('I told you so')
    logger.warning('Watch out!')
    logger.error('Error!')
    logger.critical('Critical!')