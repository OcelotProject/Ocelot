from ocelot.logger import *
import functools
import logging
import multiprocessing
import os
import time


def worker_process(n):
    logger = logging.getLogger()
    logger.info({'message': "Worker process %s started" % n})
    time.sleep(0.1)
    logger.info({'message': "Worker process %s finished" % n})


def normal_function():
    logging.info({'message': "Normal process started"})
    time.sleep(0.1)
    logging.info({'message': "Normal process finished"})


def main():
    fp, logger = create_log(os.getcwd())
    logging.info({'message': "Before starting context manager"})
    with open_queue(logger) as log_queue:

        logged_call(log_queue, normal_function)

        with multiprocessing.Pool(processes=4) as pool:
            curried = functools.partial(
                logged_call,
                log_queue,
                worker_process
            )

            curried(-1)

            pool.map(curried, range(10))

        logging.info({'message': "Logged first wave of function calls"})

        logged_call(log_queue, normal_function)

        with multiprocessing.Pool(processes=4) as pool:
            curried = functools.partial(
                logged_call,
                log_queue,
                worker_process
            )

            pool.map(curried, range(10))

        logging.info({'message': "Logged seconed wave of function calls"})


if __name__ == '__main__':
    main()
