from multiprocessing import current_process
import os
import signal

class ManualChaos:
    def __init__(self) -> None:
        self.stop_chaos = False

    def chaos(self):
        if not self.stop_chaos:
            print("Break up now? Y/n (Use S to stop chaos)\n")
            chaos = input()
            if chaos == "Y":
                process = current_process()
                os.kill(process.pid, signal.SIGTERM)
            if chaos == "S":
                self.stop_chaos = True