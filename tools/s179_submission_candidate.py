#!/usr/bin/env python3
"""Assemble an explicitly allowlisted, local draft candidate; never a release approval.

No globbing or source-directory recursion is performed. Raw/private material is
rejected even if it appears in the input list. Original files are only read.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
STATUS = 'DRAFT_CANDIDATE_NOT_AUTHOR_APPROVED'
LABELS = ['AI_DELEGATED_D085', 'NOT_INDEPENDENT',
          'NOT_HUMAN_VERIFIED_UNTIL_REVIEW', 'NO_HUMAN_SIGNOFF_D085']
OUTPUT_PREFIX = Path('data/derived/submission_candidate_2026-11-13')
EXTENSIONS = {'.md', '.json', '.csv', '.pdf', '.html', '.png', '.svg'}
PRIVATE_TOKEN = re.compile(r'private|checkpoint|ckpt|sealed|seed|\.env', re.I)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _no_symlink(root: Path, relative: Path) -> None:
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError('symlink paths are not package members or outputs')


def checked_members(root: Path, members: list[str]) -> list[tuple[str, Path]]:
    """Validate exact repository-relative public artifact files, no directories."""
    root = Path(root).resolve()
    if not members or len(members) != len({str(m).casefold() for m in members}):
        raise ValueError('nonempty, unique explicit file list required')
    result = []
    for name in members:
        if not isinstance(name, str) or not name or '\\' in name or ':' in name:
            raise ValueError('member must be a plain POSIX relative path')
        p = PurePosixPath(name)
        if p.is_absolute() or any(x in {'.', '..', ''} for x in name.split('/')):
            raise ValueError('absolute paths and traversal are forbidden')
        if p.parts[0] not in {'reports', 'handoff'} or any(x.startswith('.') for x in p.parts):
            raise ValueError('only public reports and handoff artifact paths may be included')
        if PRIVATE_TOKEN.search(name) or p.suffix.lower() not in EXTENSIONS:
            raise ValueError('private/secret/model members or unsupported extensions are forbidden')
        relative = Path(*p.parts)
        _no_symlink(root, relative)
        source = root / relative
        if not source.is_file() or not source.resolve().is_relative_to(root):
            raise ValueError('member must be an existing regular file inside the repository')
        result.append((p.as_posix(), source))
    return sorted(result)


def _checked_archive(root: Path, archive: Path) -> Path:
    archive = Path(archive)
    if not archive.is_absolute():
        archive = root / archive
    try:
        relative = archive.relative_to(root)
    except ValueError as exc:
        raise ValueError('archive must stay inside local ignored candidate directory') from exc
    if not relative.is_relative_to(OUTPUT_PREFIX) or relative.suffix != '.zip' or '..' in relative.parts:
        raise ValueError('archive must be a ZIP in the ignored candidate directory')
    _no_symlink(root, relative)
    return archive


def build(root: Path, members: list[str], archive: Path, *, revision: str) -> dict:
    """Build once and return a manifest binding the archived bytes and member bytes."""
    root = Path(root).resolve()
    checked = checked_members(root, members)
    archive = _checked_archive(root, archive)
    if archive.exists():
        raise FileExistsError('refusing to overwrite candidate archive')
    payloads = [(name, source.read_bytes()) for name, source in checked]
    records = [{'path': name, 'bytes': len(raw), 'sha256': _sha(raw)} for name, raw in payloads]
    manifest = {
        'record': 'REDUCED_SUBMISSION_DRAFT_CANDIDATE',
        'status': STATUS, 'labels': LABELS, 'source_revision': revision,
        'scientific_gate_pass': False, 'author_approval': 'NOT_SUPPLIED',
        'original_H1_H3': 'RULE_NOT_MET_RETAINED',
        'members': records,
        'limitations': [
            'Explicit artifact snapshot, not final author edits or submission approval.',
            'Original report/deck exports are earlier drafts; accompanying addenda state newer results.',
            'No raw recipes, source papers, private reviews, model files or ledgers are included.',
            'Scientific and independence limits remain unchanged; archive identity is not scientific validity.',
            'This artifact bundle is not a complete executable/data environment; use the pinned repository instructions.'
        ]
    }
    archive.parent.mkdir(parents=True, exist_ok=True)
    with archive.open('xb') as handle:
        with zipfile.ZipFile(handle, 'w', compression=zipfile.ZIP_DEFLATED) as zipped:
            def put(name, data):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                zipped.writestr(info, data)
            put('MANIFEST.json', (json.dumps(manifest, indent=2, sort_keys=True)+'\n').encode())
            for name, raw in payloads:
                put(name, raw)
    return {**manifest, 'archive_path': archive.relative_to(root).as_posix(),
            'archive_sha256': _sha(archive.read_bytes()), 'archive_bytes': archive.stat().st_size}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--allowlist', type=Path, required=True)
    ap.add_argument('--archive', type=Path, required=True)
    ap.add_argument('--manifest-out', type=Path, required=True)
    args = ap.parse_args(argv)
    config = json.loads(args.allowlist.read_text())
    if args.manifest_out.exists():
        ap.error('refusing to overwrite external manifest')
    try:
        revision = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
        report = build(ROOT, config['members'], args.archive, revision=revision)
    except (ValueError, FileExistsError, KeyError) as exc:
        ap.error(str(exc))
    args.manifest_out.parent.mkdir(parents=True, exist_ok=True)
    with args.manifest_out.open('x') as f:
        f.write(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'members': len(report['members']), 'archive_sha256': report['archive_sha256'],
                      'status': report['status']}))


if __name__ == '__main__':
    main()
