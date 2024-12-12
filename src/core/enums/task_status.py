from enum import Enum


class TaskStatus(str, Enum):
    PLANNING = "Planning"
    RESEARCH = "Research"
    IMPLEMENTATION = "Implementation"
    DONE = "Done"
    CANCELLED = "Cancelled"
    ON_HOLD = "On Hold"
    TESTING = "Testing"
    REVIEW = "Review"

    def __str__(self):
        return self.value
