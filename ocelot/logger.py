# -*- coding: utf-8 -*-
from logging.handlers import QueueHandler, QueueListener
import contextlib
import json
import logging
import multiprocessing
import os
import time


class JsonFormatter(logging.Formatter):
    """Add ``time`` field, and dump to JSON.

    Uses code from https://github.com/madzak/python-json-logger/ under BSD license."""
    def format(self, record):
        if not isinstance(record.msg, dict):
            # Messages from child processes are strings
            record.msg = eval(record.msg)
        assert isinstance(record.msg, dict)
        message_dict = record.msg
        message_dict['time'] = time.time()
        return json.dumps(message_dict, ensure_ascii=False)


def create_log(output_dir):
    """Create a JSON log file in ``output_dir``.

    Returns filepath of created log file and log handler."""
    formatter = JsonFormatter()
    filepath = os.path.join(output_dir, "report.log.json")
    handler = logging.FileHandler(filepath, encoding='utf-8')
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return filepath, handler


@contextlib.contextmanager
def queued_log(handler):
    """Start a logging queue for multiprocessing workers.

    Uses the handler created by ``create_log``.

    As a context manager, this function will start and stop the queue listener automatically.

    Usage:

    ..code-block:: python

        _, handler = create_log("some directory")
        with queued_log(handler) as queue:
            with multiprocessing.Pool(
                        initializer=worker_init,
                        initargs=[queue]
                    ) as pool:
                do_something()

    Adapted from http://stackoverflow.com/a/34964369/164864."""
    logging_queue = multiprocessing.Queue()
    queue_listener = QueueListener(logging_queue, handler)
    queue_listener.start()
    yield logging_queue
    queue_listener.stop()


def worker_init(logging_queue):
    """Change the default handler to send logging messages to a multiprocessing queue.

    This needs to be run in each child process, because of the way multiprocessing works in Windows. There
    is no `fork`, so each child process starts in a "clean" environment.

    This is only run after the logging queue has been initialized and a suitable listener constructed.

    In the main process, just call this function once to change the default logger. In a multiprocessing pool, call

    ..code-block:: python

        with multiprocessing.Pool(initializer=worker_init, initargs=[logging_queue]) as pool:

    """
    queue_handler = QueueHandler(logging_queue)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(queue_handler)
