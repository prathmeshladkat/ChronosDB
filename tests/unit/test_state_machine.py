"""Unit tests for state machine."""
import pytest
from chronosdb.core.state_machine import JobStateMachine, StepStateMachine
from chronosdb.config.constants import JobState, StepState


def test_job_state_machine_valid_transition():
    """Test valid job state transition."""
    # PENDING → RUNNING is valid
    assert JobStateMachine.can_transition(JobState.PENDING, JobState.RUNNING)
    
    # Perform transition
    new_state = JobStateMachine.transition(JobState.PENDING, JobState.RUNNING)
    assert new_state == JobState.RUNNING


def test_job_state_machine_invalid_transition():
    """Test invalid job state transition raises error."""
    # COMPLETED → RUNNING is invalid
    assert not JobStateMachine.can_transition(JobState.COMPLETED, JobState.RUNNING)
    
    # Should raise ValueError
    with pytest.raises(ValueError, match="Invalid state transition"):
        JobStateMachine.transition(JobState.COMPLETED, JobState.RUNNING)


def test_job_terminal_states():
    """Test terminal state detection."""
    assert JobStateMachine.is_terminal(JobState.COMPLETED)
    assert JobStateMachine.is_terminal(JobState.FAILED)
    assert JobStateMachine.is_terminal(JobState.CANCELLED)
    assert not JobStateMachine.is_terminal(JobState.RUNNING)


def test_step_state_machine():
    """Test step state transitions."""
    # PENDING → RUNNING → COMPLETED
    assert StepStateMachine.can_transition(StepState.PENDING, StepState.RUNNING)
    assert StepStateMachine.can_transition(StepState.RUNNING, StepState.COMPLETED)
    
    # Can't go back
    assert not StepStateMachine.can_transition(StepState.COMPLETED, StepState.RUNNING)