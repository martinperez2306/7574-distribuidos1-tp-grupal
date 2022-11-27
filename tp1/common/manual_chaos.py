from multiprocessing import current_process
import os
import signal

class ManualChaos:
    def __init__(self) -> None:
        pass

    def chaos(self):
        print("Break now? Y/n\n")
        chaos = input()
        if chaos == "Y":
            process = current_process()
            os.kill(process.pid, signal.SIGTERM)