"""Candidate packager controls on synthetic files; no project source data."""
from pathlib import Path
import hashlib
import importlib.util
import json
import zipfile
import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('candidate', ROOT / 'tools/s179_submission_candidate.py')
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)


def setup_tree(tmp_path):
    (tmp_path / 'reports/final').mkdir(parents=True)
    (tmp_path / 'reports/final/draft.md').write_text('Synthetic draft, no scientific claim.\n')
    return tmp_path


@pytest.mark.parametrize('path', ['../secret.md', '/tmp/secret.md', 'reports/../secret.md',
                                  'annotation/reviewer.csv', 'data/raw/paper.pdf',
                                  'ledgers/data/EVD.jsonl', 'reports/private_seed.txt',
                                  'reports/ckpt.pt', 'reports\\final\\draft.md'])
def test_rejects_outside_private_or_unsafe_members(tmp_path, path):
    setup_tree(tmp_path)
    with pytest.raises(ValueError):
        P.checked_members(tmp_path, [path])


def test_refuses_symlink_even_inside_allowed_directory(tmp_path):
    setup_tree(tmp_path)
    (tmp_path / 'reports/final/link.md').symlink_to('draft.md')
    with pytest.raises(ValueError):
        P.checked_members(tmp_path, ['reports/final/link.md'])


def test_manifest_binds_members_and_archive_without_overwrite(tmp_path):
    root = setup_tree(tmp_path)
    out = root / 'data/derived/submission_candidate_2026-11-13/candidate.zip'
    report = P.build(root, ['reports/final/draft.md'], out, revision='synthetic-revision')
    assert report['status'] == 'DRAFT_CANDIDATE_NOT_AUTHOR_APPROVED'
    assert report['archive_sha256'] == hashlib.sha256(out.read_bytes()).hexdigest()
    assert report['members'][0]['sha256'] == hashlib.sha256((root/'reports/final/draft.md').read_bytes()).hexdigest()
    with zipfile.ZipFile(out) as archive:
        assert set(archive.namelist()) == {'MANIFEST.json', 'reports/final/draft.md'}
        manifest = json.loads(archive.read('MANIFEST.json'))
        assert manifest['scientific_gate_pass'] is False
        assert manifest['members'] == report['members']
    original = out.read_bytes()
    with pytest.raises(FileExistsError):
        P.build(root, ['reports/final/draft.md'], out, revision='synthetic-revision')
    assert out.read_bytes() == original


def test_no_output_created_when_member_validation_fails(tmp_path):
    root = setup_tree(tmp_path)
    out = root / 'data/derived/submission_candidate_2026-11-13/candidate.zip'
    with pytest.raises(ValueError):
        P.build(root, ['reports/final/draft.md', 'annotation/reviewer.csv'], out, revision='x')
    assert not out.exists()


def test_output_must_be_local_ignored_candidate_directory(tmp_path):
    root = setup_tree(tmp_path)
    with pytest.raises(ValueError):
        P.build(root, ['reports/final/draft.md'], root/'reports/public.zip', revision='x')


def test_duplicate_members_and_empty_lists_rejected(tmp_path):
    root=setup_tree(tmp_path)
    for members in [[], ['reports/final/draft.md', 'reports/final/draft.md']]:
        with pytest.raises(ValueError):P.checked_members(root, members)
