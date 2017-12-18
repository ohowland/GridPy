class State:
    def run(self, s_input):
        assert 0, "run not implemented"

    def next(self, s_input):
        assert 0, "next not implemented"

class StateMachine:
    def __init__(self, initial_state, sm_input):
        self.currentState = initial_state
        self.currentState.run(sm_input)

    # Template method:
    def run(self, sm_input):
        self.currentState = self.currentState.next(sm_input)
        return self.currentState.run(sm_input)