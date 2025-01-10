import schedule
from threading import Thread


def scheduler(*, time=None, seconds=None):

    def run_threaded(job_func):
        job_thread = Thread(target=job_func)
        job_thread.start()

    def inner(func):
        if seconds:
            schedule.every(seconds).seconds.do(run_threaded, func)
        elif time:
            schedule.every().day.at(time).do(run_threaded, func)
            
        def wrapper():
            while True:
                schedule.run_pending()

        return wrapper

    return inner
