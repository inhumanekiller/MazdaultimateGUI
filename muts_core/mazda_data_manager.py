from collections import deque

class MazdaDataManager:
    """Factory-grade ECU data manager with queued action system"""
    def __init__(self):
        self.queued_actions = deque()

    def queue_action(self, action_name):
        self.queued_actions.append(action_name)

    def execute_queued_actions(self):
        executed = []
        while self.queued_actions:
            action = self.queued_actions.popleft()
            # Simulation: replace this with real ECU write
            print(f"Executing ECU action: {action}")
            executed.append(action)
        return executed
