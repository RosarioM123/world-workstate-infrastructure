"""Prompt 3 data model: the Task entity in the handoff layer.

Acceptance tests for docs/DATA_MODEL_PROPOSAL.md section 9. Tasks are
the typed form of what `next_actions` already recorded as free text:
an id, a lifecycle status, an owner, a parent link for subtasks, and
dependency links, all validated by `save_state` the same way decision
links are. States stored before tasks existed must still load.
"""

import pytest

from world import AgentState, Task, World, load_state, save_state
from world.handoff import project_state


def _world_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("WORLD_DIR", str(tmp_path))


def _state_with_tasks() -> AgentState:
    return AgentState(
        objective="Ship the Prompt 3 data model subset",
        tasks=[
            Task(
                title="Write the data model proposal",
                id="t-proposal",
                status="done",
                owner="agent-a",
            ),
            Task(
                title="Implement the Task entity",
                id="t-impl",
                status="in_progress",
                owner="agent-a",
                depends_on=["t-proposal"],
            ),
            Task(
                title="Write acceptance tests",
                id="t-tests",
                status="in_progress",
                owner="agent-b",
                parent_id="t-impl",
                depends_on=["t-proposal"],
            ),
        ],
        next_actions=["Land the branch on main"],
    )


def test_task_fields_roundtrip_through_save_and_load(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)
    saved = _state_with_tasks()
    seq = save_state("job-t1", saved, actor="agent-a")
    assert seq == 1

    loaded = load_state("job-t1")
    assert loaded.tasks == saved.tasks
    assert loaded == saved
    task = loaded.tasks[2]
    assert task.parent_id == "t-impl"
    assert task.depends_on == ["t-proposal"]
    assert task.owner == "agent-b"
    assert task.status == "in_progress"


def test_old_format_handoff_without_tasks_still_loads(tmp_path, monkeypatch):
    """A handoff stored before the Task entity existed (no 'tasks'
    key) loads with an empty task list instead of failing."""
    _world_dir(tmp_path, monkeypatch)
    w = World("job-t2")
    w.update(
        {
            "handoff": {
                "objective": "Legacy handoff",
                "decisions": [{"text": "Old decision", "rationale": "then"}],
                "evidence": [{"claim": "Old claim", "source": "memory"}],
                "open_questions": [],
                "next_actions": [],
            }
        },
        actor="agent-a",
    )
    loaded = load_state(w)
    assert loaded.tasks == []


def test_tasks_load_from_fresh_handle(tmp_path, monkeypatch):
    """A successor with only the world name recovers the task list."""
    _world_dir(tmp_path, monkeypatch)
    save_state("job-t3", _state_with_tasks(), actor="agent-a")
    loaded = load_state(World("job-t3"))
    assert [t.id for t in loaded.tasks] == ["t-proposal", "t-impl", "t-tests"]


def test_invalid_task_status_rejected():
    with pytest.raises(ValueError, match="task status"):
        Task(title="x", status="doing")


def test_validation_duplicate_task_ids_rejected(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)
    state = AgentState(
        objective="dup",
        tasks=[Task(title="a", id="t-1"), Task(title="b", id="t-1")],
    )
    with pytest.raises(ValueError, match="duplicate task id"):
        save_state("job-t4", state)


def test_validation_parent_must_resolve(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)
    state = AgentState(
        objective="orphan",
        tasks=[Task(title="child", id="t-1", parent_id="t-missing")],
    )
    with pytest.raises(ValueError, match="unknown parent"):
        save_state("job-t5", state)


def test_validation_task_cannot_be_own_parent(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)
    state = AgentState(
        objective="self parent",
        tasks=[Task(title="loop", id="t-1", parent_id="t-1")],
    )
    with pytest.raises(ValueError, match="own parent"):
        save_state("job-t6", state)


def test_validation_parent_cycle_rejected(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)
    state = AgentState(
        objective="parent cycle",
        tasks=[
            Task(title="a", id="t-1", parent_id="t-2"),
            Task(title="b", id="t-2", parent_id="t-1"),
        ],
    )
    with pytest.raises(ValueError, match="parent cycle"):
        save_state("job-t7", state)


def test_validation_depends_on_must_resolve(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)
    state = AgentState(
        objective="missing dep",
        tasks=[Task(title="a", id="t-1", depends_on=["t-missing"])],
    )
    with pytest.raises(ValueError, match="unknown task id"):
        save_state("job-t8", state)


def test_validation_task_cannot_depend_on_itself(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)
    state = AgentState(
        objective="self dep",
        tasks=[Task(title="a", id="t-1", depends_on=["t-1"])],
    )
    with pytest.raises(ValueError, match="depend on itself"):
        save_state("job-t9", state)


def test_validation_dependency_cycle_rejected(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)
    state = AgentState(
        objective="dep cycle",
        tasks=[
            Task(title="a", id="t-1", depends_on=["t-2"]),
            Task(title="b", id="t-2", depends_on=["t-1"]),
        ],
    )
    with pytest.raises(ValueError, match="dependency cycle"):
        save_state("job-t10", state)


def test_subtask_and_dependency_graph_roundtrip(tmp_path, monkeypatch):
    """A diamond graph (two subtasks sharing one dependency) is valid
    and survives the round trip exactly."""
    _world_dir(tmp_path, monkeypatch)
    state = AgentState(
        objective="diamond",
        tasks=[
            Task(title="base", id="t-base", status="done"),
            Task(title="left", id="t-left", parent_id="t-base", depends_on=["t-base"]),
            Task(
                title="right", id="t-right", parent_id="t-base", depends_on=["t-base"]
            ),
            Task(title="join", id="t-join", depends_on=["t-left", "t-right"]),
        ],
    )
    save_state("job-t11", state)
    assert load_state("job-t11").tasks == state.tasks


def test_project_state_compacts_finished_tasks(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)
    long_title = "word " * 40 + "end"
    state = AgentState(
        objective="projection",
        tasks=[
            Task(title=long_title, id="t-done", status="done", owner="agent-a"),
            Task(
                title="Still running task",
                id="t-live",
                status="blocked",
                owner="agent-b",
                depends_on=["t-done"],
            ),
        ],
    )
    projected = project_state(state)
    done, live = projected.tasks
    assert done.status == "done" and done.id == "t-done"
    assert done.owner == "agent-a"
    assert len(done.title) <= 100 and done.title != long_title
    assert live.title == "Still running task"
    assert live.depends_on == ["t-done"]
    # The input is not mutated.
    assert state.tasks[0].title == long_title
