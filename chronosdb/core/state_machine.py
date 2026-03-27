"""
State mschinr for job and step transitions.

what is a State Machine?
-A system that can be in one of several states
-Transitions between states follow strict rules
-Example a door can OPEN or CLOSED but not both

Why use it?
-Prevents invalid states (eg. can't complete a job that hasn't started)
-clear buisness rules
-Easy to test
"""

from typing import Set, Dict
from chronosdb.config.constants import JobState, StepState

class JobStateMachine:
    """
    Managae valid state transition for Jobs.

    Valid transitions:
    PENDING -> RUNNING ->COMPLETED
    PENDING -> RUNNING -> FAILED
    RUNNING -> WAITING (delayed step)
    RUNNING -> retrying ->RUNNING
    ANY -> PAUSED -> RUNNING 
    ANY -> CANCELLED 
    """

    # Define which states can transition to which
    TRANSITIONS: Dict[JobState, Set[JobState]] = {
        JobState.PENDING: {
            JobState.RUNNING,
            JobState.CANCELLED,
        },
        JobState.RUNNING: {
            JobState.WAITING,
            JobState.RETRYING,
            JobState.COMPLETED,
            JobState.FAILED,
            JobState.PAUSED,
            JobState.CANCELLED,
        },
        JobState.WAITING: {
            JobState.RUNNING,
            JobState.CANCELLED,
        },
        JobState.RETRYING: {
            JobState.RUNNING,
            JobState.FAILED,
            JobState.CANCELLED,
        },
        JobState.PAUSED: {
            JobState.RUNNING,
            JobState.CANCELLED,
        },
        JobState.COMPLETED: set(),  # Terminal state - can't transition
        JobState.FAILED: set(),     # Terminal state - can't transition
        JobState.CANCELLED: set(),  # Terminal state - can't transition
    }

    @classmethod
    def can_transition(cls, from_state, to_state: JobState) -> bool:
        """
        check if transition is valid

        Args: 
           from_state: current state
           to_state: Desired new state

        Returns:
            True if transition is allowed, False otherwise

        Example:
            >>>JobStateMachine.can_transition(JobState.PENDING, JobState.RUNNING)
            True
            >>>JobStateMachine.can_transition(JobState.COMPLETED, JobState.RUNNING)
            False
        """
        allowed_transactions = cls.TRANSITIONS.get(from_state, set())
        return to_state in allowed_transactions
    
    @classmethod
    def transition(cls, from_state: JobState, to_state: JobState) -> JobState:
        """
        Perform state transitions with validations.

        Args:
            from_state: Current state
            to_state: Desired new state

        Return:
            The new state

        Raises:
            ValueError: if transition is not allowed

        Example:
            >>> new_state = JobStateMachine.transition(JobState.PENDING, JobState.RUNNING)
            >>> print(new_state)
            JobState.RUNNING
        """

        if not cls.can_transition(from_state, to_state):
            raise ValueError(
                f"Invalid state transition: {from_state.value} -> {to_state.value}"
            )
        return to_state
    
    @classmethod
    def is_terminal(cls, state: JobState) -> bool:
        """
        Check if state is terminal (no further transition possible).

        Args:
            state: state to check

        Returns:
            True if terminal, False otherwise
        """

        return state in {JobState.COMPLETED, JobState.FAILED, JobState.CANCELLED}
    
class StepStateMachine:
    """
    Manages valid state transitions for Steps.
    
    Simpler than Job state machine:
    PENDING → RUNNING → COMPLETED
    PENDING → RUNNING → FAILED
    PENDING → SKIPPED (if conditional logic skips it)
    """
    
    TRANSITIONS: Dict[StepState, Set[StepState]] = {
        StepState.PENDING: {
            StepState.RUNNING,
            StepState.SKIPPED,
        },
        StepState.RUNNING: {
            StepState.COMPLETED,
            StepState.FAILED,
        },
        StepState.COMPLETED: set(),  # Terminal
        StepState.FAILED: set(),     # Terminal
        StepState.SKIPPED: set(),    # Terminal
    }
    
    @classmethod
    def can_transition(cls, from_state: StepState, to_state: StepState) -> bool:
        """Check if step state transition is valid."""
        allowed_transitions = cls.TRANSITIONS.get(from_state, set())
        return to_state in allowed_transitions
    
    @classmethod
    def transition(cls, from_state: StepState, to_state: StepState) -> StepState:
        """Perform step state transition with validation."""
        if not cls.can_transition(from_state, to_state):
            raise ValueError(
                f"Invalid step state transition: {from_state.value} → {to_state.value}"
            )
        return to_state
    
    @classmethod
    def is_terminal(cls, state: StepState) -> bool:
        """Check if step state is terminal."""
        return state in {StepState.COMPLETED, StepState.FAILED, StepState.SKIPPED}