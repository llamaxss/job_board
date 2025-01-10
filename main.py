from scheduler import scheduler


def start_process() -> None:
    from process import start

    start()


if __name__ == "__main__":

    @scheduler(time="15:00")
    def run():
        start_process()

    run()
