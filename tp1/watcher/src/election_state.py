PARTICIPATING = 'P'
NOT_PARTICIPATING = 'NP'

class ElectionState:
    def __init__(self, type, id) -> None:
        self.CODE = None
        self.type = type
        self.id = id

class Participating(ElectionState):
    def __init__(self) -> None:
        self.CODE = PARTICIPATING
    
    @staticmethod
    def is_state(election: ElectionState) -> bool:
        return election.id == PARTICIPATING

class NotParticipating(ElectionState):
    def __init__(self) -> None:
        self.CODE = NOT_PARTICIPATING
    
    @staticmethod
    def is_state(election: ElectionState) -> bool:
        return election.id == NOT_PARTICIPATING