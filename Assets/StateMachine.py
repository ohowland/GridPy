class State:
    def run(self, input, output):
        assert 0, "run not implemented"

    def next(self, input):
        assert 0, "next not implemented"

class StateMachine:
    def __init__(self, initialState, smInput, smOutput):
        self.currentState = initialState
        self.currentState.run(smInput, smOutput)

    # Template method:
    def run(self, smInput, smOutput):
        self.currentState = self.currentState.next(smInput)
        return self.currentState.run(smInput, smOutput)