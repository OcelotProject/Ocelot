# -*- coding: utf-8 -*-

# Uses a great deal of code from
# https://gist.github.com/schlamar/7003737

import contextlib
import json
import logging
import multiprocessing
import os
import threading
import time


class JsonFormatter(logging.Formatter):
    """Uses code from https://github.com/madzak/python-json-logger/ under BSD license"""
    def format(self, record):
        assert isinstance(record.msg, dict)
        message_dict = record.msg
        message_dict['time'] = time.time()
        return json.dumps(message_dict, ensure_ascii=False)


def create_log(output_dir):
    logger = logging.getLogger('ocelot')
    formatter = JsonFormatter()
    filepath = os.path.join(output_dir, "report.log.json")
    handler = logging.FileHandler(filepath, encoding='utf-8')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return filepath, logger


def daemon(log_queue, logger):
    """Daemon process that listens to the log queue and write messages to the log file"""
    while True:
        try:
            record_data = log_queue.get()
            if record_data is None:
                # Send None to kill daemon process
                break
            record = logging.makeLogRecord(record_data)
            print("Received log message: ", record)
            print("Logger:", logger)
            logger.handle(record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except EOFError:
            break
        except:
            logging.exception('Error in log handler.')


@contextlib.contextmanager
def open_queue(logger):
    # Queue for log messages that is written to by child processes
    # Have to use a manager to share among processes
    manager = multiprocessing.Manager()
    log_queue = manager.Queue()
    # New thread that handles the messages in order to avoid multiple
    # writers causing log corruption
    daemon_thread = threading.Thread(target=daemon, args=(log_queue, logger))
    daemon_thread.start()
    yield log_queue
    # Sending None kills the daemon thread
    log_queue.put(None)


class MPLogger(logging.Logger):
    log_queue = None

    def isEnabledFor(self, level):
        return True

    def handle(self, record):
        # Special handling for exceptions because we will put them on the Queue
        # But exceptions can't be pickled. We have to format them in advance.
        print("Received message in `MPLogger.handle`:", record)
        ei = record.exc_info
        if ei:
            # to get traceback text into record.exc_text
            logging._defaultFormatter.format(record)
            record.exc_info = None  # not needed any more
        d = dict(record.__dict__)
        d['msg'] = record.getMessage()
        d['args'] = None
        self.log_queue.put(d)


def logged_call(log_queue, function, *args, **kwargs):
    MPLogger.log_queue = log_queue
    logging.setLoggerClass(MPLogger)
    # Monkey patch root logger and already defined loggers
    # to send all messags to `log_queue`
    logging.root.__class__ = MPLogger
    print("Loggers:", logging.Logger.manager.loggerDict)
    for key, logger in logging.Logger.manager.loggerDict.items():
        if key == 'ocelot':
            continue
        elif not isinstance(logger, logging.PlaceHolder):
            logger.__class__ = MPLogger
    # Then call the function
    return function(*args, **kwargs)


