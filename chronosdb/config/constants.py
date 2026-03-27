from enum import Enum

class JobState(Enum):
    """Job lifecycle states."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    RETRYING = "RETRYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"

class StepState(Enum):
    """step execution states."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

class ExecutionStatus(str, Enum):
    """Individual step execution attempt status."""
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"

class TriggerType(str, Enum):
    """who/what triggered the job"""
    PENDING = "PENDING"
    MANUAL = "MANUAL"          #human via api
    SCHEDULED = "SCHEDULED"    #cron/timer
    WEBHOOK = "WEBHOOK"        #external event
    AI_AGENT = "AI_AGENT"       #ai aggent decision
    REPLAY = "REPLAY"           #manual replay
    RETRY = "RETRY"


class StepType(str, Enum):
    """Types of steps"""
    TASK = "TASK"              # Regular task execution
    LLM_CALL = "LLM_CALL"      # Call to LLM API
    DECISION = "DECISION"      # AI-driven routing/branching
    HUMAN_IN_LOOP = "HUMAN_IN_LOOP"  # Wait for human approval
    WEBHOOK = "WEBHOOK"        # HTTP callback
    DELAY = "DELAY"  