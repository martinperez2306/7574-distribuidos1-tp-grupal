import sys
class ManualChaos:
    def __init__(self) -> None:
        pass

    @staticmethod
    def chaos():
        print("Break now? Y/n\n")
        chaos = input()
        if chaos == "Y":
            sys.exit(1)