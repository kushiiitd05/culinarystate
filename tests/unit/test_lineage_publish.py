import pytest

from culinarystate.lineage import publish


def _mk(tmp_path, real, scratch):
    r, s = tmp_path / "real", tmp_path / "scratch"
    for d, files in ((r, real), (s, scratch)):
        d.mkdir(parents=True)
        for n, b in files.items():
            (d / n).write_bytes(b)
    return r, s


def test_plan_allows_new_file_and_appends(tmp_path):
    r, s = _mk(tmp_path, {"STUDY.jsonl": b"a\n", "_ids.jsonl": b"x\n", "EVD.jsonl": b"e\n"},
               {"STUDY.jsonl": b"a\nb\n", "_ids.jsonl": b"x\ny\n", "EVD.jsonl": b"e\n", "DOC.jsonl": b"d\n"})
    plan = publish.plan_publish(r, s)
    assert plan == {"new": ["DOC.jsonl"], "append": ["STUDY.jsonl", "_ids.jsonl"]}


def test_plan_refuses_changed_protected_or_non_prefix(tmp_path):
    r, s = _mk(tmp_path, {"EVD.jsonl": b"e\n", "STUDY.jsonl": b"a\n"}, {"EVD.jsonl": b"E\n", "STUDY.jsonl": b"a\n"})
    with pytest.raises(publish.PublishRefused):
        publish.plan_publish(r, s)
    r, s = _mk(tmp_path / "t", {"STUDY.jsonl": b"a\n"}, {"STUDY.jsonl": b"z\nb\n"})
    with pytest.raises(publish.PublishRefused):
        publish.plan_publish(r, s)


def test_apply_writes_and_is_exact(tmp_path):
    r, s = _mk(tmp_path, {"STUDY.jsonl": b"a\n"}, {"STUDY.jsonl": b"a\nb\n", "DOC.jsonl": b"d\n"})
    publish.apply_publish(r, s, publish.plan_publish(r, s))
    assert (r / "STUDY.jsonl").read_bytes() == b"a\nb\n" and (r / "DOC.jsonl").read_bytes() == b"d\n"


def test_new_file_must_not_exist(tmp_path):
    r, s = _mk(tmp_path, {"DOC.jsonl": b"old\n"}, {"DOC.jsonl": b"new\n"})
    with pytest.raises(publish.PublishRefused):
        publish.plan_publish(r, s)
