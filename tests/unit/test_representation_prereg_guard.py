"""G35-PRE guard tests. Synthetic fixtures in tmp_path only."""
import hashlib
import json

import pytest

from culinarystate.representation.prereg_guard import (
    PreregNotSigned,
    evaluation_entry,
    require_signed_prereg,
    sign_record_template,
)


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


@pytest.fixture
def doc(tmp_path):
    p = tmp_path / "prereg.md"
    p.write_text("synthetic preregistration\n", encoding="utf-8")
    return p


def _write(path, **over):
    rec = {"sha256": None, "signers": ["Synthetic A", "Synthetic B"], "date": "2026-11-01"}
    rec.update(over)
    path.write_text(json.dumps(rec), encoding="utf-8")


def test_missing_hash_file(doc, tmp_path):
    with pytest.raises(PreregNotSigned, match="hash file"):
        require_signed_prereg(doc, tmp_path / "nope.json")


def test_missing_document(tmp_path):
    h = tmp_path / "h.json"
    _write(h, sha256="0" * 64)
    with pytest.raises(PreregNotSigned):
        require_signed_prereg(tmp_path / "gone.md", h)


def test_unparseable_hash_file(doc, tmp_path):
    h = tmp_path / "h.json"
    h.write_text("not json")
    with pytest.raises(PreregNotSigned):
        require_signed_prereg(doc, h)


def test_no_sha_recorded(doc, tmp_path):
    h = tmp_path / "h.json"
    rec = {"signers": ["A"], "date": "2026-11-01"}
    h.write_text(json.dumps(rec))
    with pytest.raises(PreregNotSigned, match="sha256"):
        require_signed_prereg(doc, h)


def test_wrong_hash(doc, tmp_path):
    h = tmp_path / "h.json"
    _write(h, sha256="0" * 64)
    with pytest.raises(PreregNotSigned, match="differs"):
        require_signed_prereg(doc, h)


def test_edited_after_signing(doc, tmp_path):
    h = tmp_path / "h.json"
    _write(h, sha256=_sha(doc))
    require_signed_prereg(doc, h)
    doc.write_text("synthetic preregistration EDITED\n", encoding="utf-8")
    with pytest.raises(PreregNotSigned, match="differs"):
        require_signed_prereg(doc, h)


def test_template_is_unsigned_and_rejected(doc, tmp_path):
    h = tmp_path / "h.json"
    tpl = sign_record_template(doc)
    assert tpl["sha256"] == _sha(doc)
    assert tpl["signers"] == [] and tpl["date"] == ""
    assert "UNSIGNED" in tpl["status"]
    h.write_text(json.dumps(tpl))
    with pytest.raises(PreregNotSigned, match="signer"):
        require_signed_prereg(doc, h)


def test_template_takes_no_signer_args(doc):
    with pytest.raises(TypeError):
        sign_record_template(doc, signers=["X"], date="2026-11-01")


@pytest.mark.parametrize("signers", [[], [""], ["<NAME>"], "Kush", [" "]])
def test_bad_signers(doc, tmp_path, signers):
    h = tmp_path / "h.json"
    _write(h, sha256=_sha(doc), signers=signers)
    with pytest.raises(PreregNotSigned, match="signer"):
        require_signed_prereg(doc, h)


@pytest.mark.parametrize("date", ["", "yesterday", "2026-13-40", None])
def test_bad_date(doc, tmp_path, date):
    h = tmp_path / "h.json"
    _write(h, sha256=_sha(doc), date=date)
    with pytest.raises(PreregNotSigned, match="date"):
        require_signed_prereg(doc, h)


def test_valid_signed_fixture(doc, tmp_path):
    h = tmp_path / "h.json"
    _write(h, sha256=_sha(doc))
    assert require_signed_prereg(doc, h) == _sha(doc)


def test_decorator_blocks_then_allows(doc, tmp_path):
    h = tmp_path / "h.json"
    calls = []

    @evaluation_entry
    def run(x):
        calls.append(x)
        return x * 2

    with pytest.raises(PreregNotSigned):
        run(2, prereg_path=doc, hash_file=h)
    assert calls == []
    _write(h, sha256=_sha(doc))
    assert run(2, prereg_path=doc, hash_file=h) == 4
    assert calls == [2]


def test_two_distinct_signers_required_by_default(doc, tmp_path):
    h = tmp_path / "h.json"
    for signers in (["Kush"], ["Kush", "kush"], ["Kush", " Kush "]):
        _write(h, sha256=_sha(doc), signers=signers)
        with pytest.raises(PreregNotSigned):
            require_signed_prereg(doc, h)


def test_single_signer_needs_a_recorded_override_reason(doc, tmp_path):
    h = tmp_path / "h.json"
    _write(h, sha256=_sha(doc), signers=["Kush"], single_signer_override={"reason": "", "by": "Kush"})
    with pytest.raises(PreregNotSigned):
        require_signed_prereg(doc, h)
    _write(h, sha256=_sha(doc), signers=["Kush"], single_signer_override={"reason": "second author away", "by": "Kush"})
    assert require_signed_prereg(doc, h) == _sha(doc)


def test_bound_lookup_edit_invalidates_a_signed_synthetic_package(doc, tmp_path):
    lookup = tmp_path / "lookup.csv"
    lookup.write_text("synthetic lookup\n")
    h = tmp_path / "h.json"
    rec = sign_record_template(doc, bound_files=[lookup])
    rec.update(status="SIGNED", signers=["Synthetic A", "Synthetic B"], date="2026-10-28")
    h.write_text(json.dumps(rec))
    assert require_signed_prereg(doc, h, required_files=[lookup]) == _sha(doc)
    lookup.write_text("changed lookup\n")
    with pytest.raises(PreregNotSigned, match="bound file"):
        require_signed_prereg(doc, h, required_files=[lookup])


def test_required_lookup_cannot_be_omitted_from_hash_record(doc, tmp_path):
    lookup = tmp_path / "lookup.csv"
    lookup.write_text("synthetic lookup\n")
    h = tmp_path / "h.json"
    _write(h, sha256=_sha(doc))
    with pytest.raises(PreregNotSigned, match="required bound"):
        require_signed_prereg(doc, h, required_files=[lookup])


def test_bound_file_paths_survive_relocating_the_whole_package(doc, tmp_path):
    import shutil
    lookup = tmp_path / "lookup.csv"
    lookup.write_text("synthetic lookup\n")
    h = tmp_path / "h.json"
    rec = sign_record_template(doc, bound_files=[lookup])
    rec.update(status="SIGNED", signers=["Synthetic A", "Synthetic B"], date="2026-10-28")
    h.write_text(json.dumps(rec))
    dest = tmp_path / "relocated"
    dest.mkdir()
    for path in (doc, lookup, h):
        shutil.copyfile(path, dest / path.name)
    assert require_signed_prereg(dest / doc.name, dest / h.name,
                                 required_files=[dest / lookup.name]) == _sha(doc)


@pytest.mark.parametrize("bad", [None, {}, [{"path": "missing", "sha256": "0" * 64}],
                                [{"path": "lookup.csv", "sha256": "UNKNOWN"}]])
def test_malformed_or_missing_bound_files_are_refused(doc, tmp_path, bad):
    h = tmp_path / "h.json"
    _write(h, sha256=_sha(doc), bound_files=bad)
    with pytest.raises(PreregNotSigned, match="bound"):
        require_signed_prereg(doc, h)


def test_decorator_checks_required_bound_files_before_function_runs(doc, tmp_path):
    lookup = tmp_path / "lookup.csv"
    lookup.write_text("synthetic lookup\n")
    h = tmp_path / "h.json"
    _write(h, sha256=_sha(doc))
    calls = []

    @evaluation_entry
    def run():
        calls.append(True)

    with pytest.raises(PreregNotSigned, match="required bound"):
        run(prereg_path=doc, hash_file=h, prereg_required_files=[lookup])
    assert not calls
