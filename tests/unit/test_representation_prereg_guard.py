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
