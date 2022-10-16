from enum import Enum


class ResourceType(str, Enum):
    JOBS = "jobs"
    STEPS = "steps"
