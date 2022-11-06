LEADER = 'L'
LEADER_ELECTION = 'LE'
LEADER_SELECTED = 'LS'

class Election:
    def __init__(self, type, id) -> None:
        self.CODE = None
        self.type = type
        self.id = id

    def pack(self):
        return f'{self.CODE}'

    @staticmethod
    def of(message: str):
        split = message.split("_")
        return Election(split[0], split[1])

    def to_string(self) -> str:
        return self.type + "_" + self.id

class Leader(Election):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.CODE = LEADER
    
    @staticmethod
    def is_election(election: Election) -> bool:
        return election.id == LEADER

class LeaderElection(Election):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.CODE = LEADER_ELECTION

    @staticmethod
    def is_election(election: Election) -> bool:
        return election.id == LEADER_ELECTION

class LeaderSelected(Election):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.CODE = LEADER_SELECTED

    @staticmethod
    def is_election(election: Election) -> bool:
        return election.id == LEADER_SELECTED