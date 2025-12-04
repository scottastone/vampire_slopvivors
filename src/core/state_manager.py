class StateManager:
    def __init__(self):
        self.state = "PLAYING" # Default state
        self.previous_state = None

    def change_state(self, new_state):
        self.previous_state = self.state
        self.state = new_state
        print(f"State changed to: {self.state}")

    def get_state(self):
        return self.state

    def is_state(self, state_check):
        return self.state == state_check
