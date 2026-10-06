#!/usr/bin/env python3
"""Restore memory permalinks that racing basic-memory watchers suffixed with "-N".

Before persistmind turned basic-memory's file watcher off (.mcp.json), every
open Claude Code session ran its own watcher on every project. When several
registered the same new note at once, one could find the note's permalink
already taken by the note itself and give it a new one ending in "-1", "-2",
written back into the frontmatter.

A file is a candidate when the last segment of its frontmatter permalink is
the slug basic-memory derives from the file name followed by "-<digits>":
feedback_foo.md with ".../feedback-foo-1". Comparing with the file-name slug,
not with a pattern on the trailing number, keeps legitimate slugs that end
with a date (".../decision-x-2026-09-08") out. The suffix is removed only when
no other entity of the project (database) and no other file of the project
(frontmatter) uses the shorter permalink.

Every touched project is then reindexed through hooks/reindex_memory.py and
checked: `basic-memory status` must report no pending change, and each fixed
file's entity must carry the restored permalink. Files whose database row
disagrees with their frontmatter permalink (for instance in a second
basic-memory config that indexes the same folders) are touched and their
stored checksum is cleared, so the incremental reindex re-reads them; they are
checked the same way.

Dry run by default; --apply writes. Refuses to write while a basic-memory MCP
server with its file watcher on is running, since it would race the fix.
Honors BASIC_MEMORY_CONFIG_DIR and PM_BASIC_MEMORY_BIN like the hooks. Needs
basic-memory's Python (for its slug function); started with another
interpreter, it re-executes itself with the one basic-memory runs on.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

BM = os.environ.get('PM_BASIC_MEMORY_BIN', 'basic-memory')


def reexec_with_basic_memory_python() -> None:
    """Re-run this script with the interpreter of the basic-memory launcher."""
    launcher = shutil.which(BM)
    shebang = ''
    if launcher:
        with open(launcher, 'rb') as fh:
            shebang = fh.readline().decode(errors='replace').strip()
    interpreter = shebang[2:].strip() if shebang.startswith('#!') else ''
    if not interpreter or not os.path.isfile(interpreter) or os.path.realpath(interpreter) == os.path.realpath(sys.executable):
        sys.exit(f"Cannot import basic_memory. Run this script with basic-memory's Python "
                 f"(the interpreter in the first line of {launcher or BM}).")
    os.execv(interpreter, [interpreter, os.path.abspath(__file__), *sys.argv[1:]])


try:
    import frontmatter
    import yaml
    from basic_memory.utils import generate_permalink
except ImportError:
    reexec_with_basic_memory_python()
    raise

BM_CONFIG_DIR = Path(os.path.expanduser(os.environ.get('BASIC_MEMORY_CONFIG_DIR') or '~/.basic-memory'))
BM_DB = BM_CONFIG_DIR / 'memory.db'
REINDEX = Path(__file__).resolve().parent.parent / 'hooks' / 'reindex_memory.py'
SUFFIX_RE = r'((?:-\d+)+)'
PERMALINK_LINE_RE = re.compile(r'^(permalink:[ \t]*)(["\']?)(.*?)\2[ \t]*$')


@dataclass
class Fix:
    project: str
    root: Path
    rel: str
    old: str
    new: str


@dataclass
class ProjectSurvey:
    name: str
    root: Path
    project_id: int
    fixes: list[Fix] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    db_mismatches: list[str] = field(default_factory=list)
    mismatched: list[str] = field(default_factory=list)
    unreadable: list[str] = field(default_factory=list)


def leading_blocks(lines: list[str]) -> list[tuple[int, int]]:
    """(start, end) line indexes of the frontmatter blocks at the top of a file:
    basic-memory may have prepended its own block above an unreadable one."""
    blocks: list[tuple[int, int]] = []
    i = 0
    while i < len(lines) and lines[i].strip() == '---':
        j = i + 1
        while j < len(lines) and lines[j].strip() != '---':
            j += 1
        if j >= len(lines):
            break
        blocks.append((i, j))
        i = j + 1
        while i < len(lines) and lines[i].strip() == '':
            i += 1
    return blocks


def rewrite_permalink(text: str, old: str, new: str) -> str | None:
    """Replace the `permalink: old` lines of the leading frontmatter blocks,
    keeping every other byte. None when the first block has no such line."""
    lines = text.splitlines(keepends=True)
    blocks = leading_blocks(lines)
    replaced_in_first = False
    for n, (start, end) in enumerate(blocks):
        for k in range(start + 1, end):
            body = lines[k].rstrip('\r\n')
            m = PERMALINK_LINE_RE.match(body)
            if m and m.group(3) == old:
                lines[k] = f'{m.group(1)}{m.group(2)}{new}{m.group(2)}' + lines[k][len(body):]
                replaced_in_first = replaced_in_first or n == 0
    return ''.join(lines) if replaced_in_first else None


def frontmatter_permalink(path: Path) -> tuple[str | None, bool]:
    """(permalink of the first frontmatter block, readable?)."""
    try:
        meta = frontmatter.loads(path.read_text(encoding='utf-8')).metadata
    except (OSError, UnicodeDecodeError, yaml.YAMLError, ValueError):
        return None, False
    value = meta.get('permalink')
    return (value if isinstance(value, str) else None), True


def load_projects(db: sqlite3.Connection) -> list[ProjectSurvey]:
    with open(BM_CONFIG_DIR / 'config.json') as fh:
        config = json.load(fh)
    ids = {name: pid for pid, name in db.execute('SELECT id, name FROM project')}
    projects: list[ProjectSurvey] = []
    for name, entry in (config.get('projects') or {}).items():
        path = entry.get('path') if isinstance(entry, dict) else entry
        if not isinstance(path, str) or not os.path.isabs(os.path.expanduser(path)) or name not in ids:
            continue
        root = Path(os.path.realpath(os.path.expanduser(path)))
        if root.is_dir():
            projects.append(ProjectSurvey(name=name, root=root, project_id=ids[name]))
    return projects


def survey(project: ProjectSurvey, db: sqlite3.Connection) -> None:
    files: dict[str, str | None] = {}
    for path in sorted(project.root.rglob('*.md')):
        rel = path.relative_to(project.root)
        if any(part.startswith('.') for part in rel.parts):
            continue
        permalink, readable = frontmatter_permalink(path)
        if not readable:
            project.unreadable.append(rel.as_posix())
        files[rel.as_posix()] = permalink
    by_permalink: dict[str, list[str]] = {}
    for rel, permalink in files.items():
        if permalink:
            by_permalink.setdefault(permalink, []).append(rel)
    db_permalinks = dict(db.execute('SELECT file_path, permalink FROM entity WHERE project_id = ?',
                                    (project.project_id,)).fetchall())
    candidates: list[Fix] = []
    for rel, permalink in files.items():
        if not permalink:
            continue
        if rel in db_permalinks and db_permalinks[rel] != permalink:
            project.db_mismatches.append(f'{rel}: file {permalink} / database {db_permalinks[rel]}')
            project.mismatched.append(rel)
        stem = generate_permalink(Path(rel).name)
        last = permalink.rpartition('/')[2]
        m = re.fullmatch(re.escape(stem) + SUFFIX_RE, last)
        if m:
            target = permalink[:len(permalink) - len(m.group(1))]
            candidates.append(Fix(project.name, project.root, rel, permalink, target))
    targets: dict[str, int] = {}
    for fix in candidates:
        targets[fix.new] = targets.get(fix.new, 0) + 1
    for fix in candidates:
        other_files = [r for r in by_permalink.get(fix.new, []) if r != fix.rel]
        other_entities = [r for (r,) in db.execute(
            'SELECT file_path FROM entity WHERE project_id = ? AND permalink = ? AND file_path != ?',
            (project.project_id, fix.new, fix.rel))]
        if targets[fix.new] > 1:
            project.skipped.append(f'{fix.rel}: {fix.new} is the target of {targets[fix.new]} files')
        elif other_files:
            project.skipped.append(f'{fix.rel}: {fix.new} is in the frontmatter of {other_files[0]}')
        elif other_entities:
            project.skipped.append(f'{fix.rel}: {fix.new} belongs to the entity of {other_entities[0]}')
        else:
            project.fixes.append(fix)


def watcher_processes(roots: list[Path]) -> list[str]:
    """basic-memory MCP servers whose file watcher is on and covers one of
    `roots` (whatever their config dir), as printable lines."""
    try:
        listing = subprocess.run(['ps', '-axo', 'pid=,command='], capture_output=True, text=True).stdout
    except OSError:
        return []
    found: list[str] = []
    for line in listing.splitlines():
        pid, _, command = line.strip().partition(' ')
        argv = command.split()
        if 'mcp' not in argv or not any(Path(a).name in ('basic-memory', 'bm') for a in argv):
            continue
        if Path(argv[0]).name in ('uv', 'uvx'):
            continue  # launcher; its python child is listed on its own
        env = process_env(pid)
        config_dir = Path(os.path.expanduser(env.get('BASIC_MEMORY_CONFIG_DIR') or '~/.basic-memory'))
        try:
            config = json.loads((config_dir / 'config.json').read_text())
        except (OSError, ValueError):
            config = {}
        if env.get('BASIC_MEMORY_SYNC_CHANGES') is not None:
            sync_on = env['BASIC_MEMORY_SYNC_CHANGES'].strip().lower() in ('1', 'true', 'yes', 'on')
        else:
            sync_on = bool(config.get('sync_changes', True))
        watched = [Path(os.path.realpath(os.path.expanduser(e['path'])))
                   for e in (config.get('projects') or {}).values()
                   if isinstance(e, dict) and isinstance(e.get('path'), str) and e['path']]
        overlaps = any(w == r or w in r.parents or r in w.parents for w in watched for r in roots)
        if sync_on and (overlaps or not config):
            found.append(f'  pid {pid} (config {config_dir}): {command[:100]}')
    return found


def process_env(pid: str) -> dict[str, str]:
    """Environment of a process of the same user (Linux /proc, else `ps eww`)."""
    proc = Path(f'/proc/{pid}/environ')
    if proc.exists():
        try:
            pairs = proc.read_bytes().split(b'\0')
            return dict(p.decode(errors='replace').split('=', 1) for p in pairs if b'=' in p)
        except OSError:
            return {}
    try:
        out = subprocess.run(['ps', 'eww', '-o', 'command=', '-p', pid], capture_output=True, text=True).stdout
    except OSError:
        return {}
    return dict(tok.split('=', 1) for tok in out.split() if re.match(r'^[A-Z_][A-Z0-9_]*=', tok))


def apply_fix(fix: Fix) -> bool:
    path = fix.root / fix.rel
    text = path.read_text(encoding='utf-8')
    updated = rewrite_permalink(text, fix.old, fix.new)
    if updated is None:
        return False
    # Temp file ends in .tmp, which basic-memory always ignores.
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.pm-fix-', suffix='.tmp')
    with os.fdopen(fd, 'w', encoding='utf-8', newline='') as fh:
        fh.write(updated)
    shutil.copymode(path, tmp)
    os.replace(tmp, path)
    return True


def reindex_and_status(project: ProjectSurvey) -> bool:
    """Reindex under the persistmind lock, then require a clean status."""
    run = subprocess.run([sys.executable, str(REINDEX), '--path', str(project.root)],
                         capture_output=True, text=True)
    print('    ' + (run.stdout.strip().splitlines() or [''])[0])
    status = subprocess.run([BM, 'status', '--project', project.name, '--json'],
                            capture_output=True, text=True)
    try:
        pending = json.loads(status.stdout).get('total', -1)
    except ValueError:
        pending = -1
    if run.returncode != 0 or pending != 0:
        print(f'    status not clean (pending changes: {pending}); reindex exit {run.returncode}')
        return False
    print('    status: No changes')
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description='Restore permalinks suffixed with "-N" by racing watchers.')
    parser.add_argument('--apply', action='store_true', help='write the fixes (default: dry run)')
    parser.add_argument('--project', action='append', default=[], help='limit to this project (repeatable)')
    parser.add_argument('--force', action='store_true', help='write even if a watcher is running')
    parser.add_argument('-v', '--verbose', action='store_true', help='list every fix and skipped file')
    args = parser.parse_args()

    db = sqlite3.connect(f'file:{BM_DB}?mode=ro', uri=True)
    projects = [p for p in load_projects(db) if not args.project or p.name in args.project]
    for project in projects:
        survey(project, db)
    db.close()

    total = sum(len(p.fixes) for p in projects)
    print(f'basic-memory config: {BM_CONFIG_DIR}')
    for p in projects:
        if p.fixes or p.skipped or p.db_mismatches or p.unreadable:
            print(f'{p.name}: {len(p.fixes)} to fix, {len(p.skipped)} skipped, '
                  f'{len(p.db_mismatches)} file/database mismatches, {len(p.unreadable)} unreadable frontmatter')
            for fix in p.fixes if args.verbose else []:
                print(f'    {fix.rel}: {fix.old} -> {fix.new}')
            for line in p.skipped:
                print(f'    skipped {line}')
            for line in p.db_mismatches if args.verbose else []:
                print(f'    mismatch {line}')
    print(f'Total: {total} permalinks to fix.')
    to_reindex = [p for p in projects if p.fixes or p.db_mismatches]
    if not args.apply:
        print('Dry run: nothing written. Re-run with --apply.')
        return 0

    watchers = watcher_processes([p.root for p in to_reindex])
    if watchers and not args.force:
        print('basic-memory MCP servers with the file watcher on are running; they would race the fix:')
        print('\n'.join(watchers))
        print('Restart those Claude Code sessions with the updated plugin first, or pass --force.')
        return 1

    ok = True
    for p in to_reindex:
        written = [f for f in p.fixes if apply_fix(f)]
        for f in p.fixes:
            if f not in written:
                print(f'    not rewritten (unexpected frontmatter layout): {f.rel}')
                ok = False
        # The incremental reindex re-reads a file only when its mtime moved and
        # its checksum differs from the stored one, so a file whose database row
        # disagrees but whose content nobody changed would stay stale. Touch it
        # and clear the stored checksum (basic-memory's own "not synced yet").
        if p.mismatched:
            con = sqlite3.connect(BM_DB, timeout=10)
            with con:
                for rel in p.mismatched:
                    os.utime(p.root / rel)
                    con.execute('UPDATE entity SET checksum = NULL WHERE project_id = ? AND file_path = ?',
                                (p.project_id, rel))
            con.close()
        print(f'{p.name}: {len(written)} rewritten, reindexing...')
        ok = reindex_and_status(p) and ok
        if written or p.mismatched:
            db = sqlite3.connect(f'file:{BM_DB}?mode=ro', uri=True)
            for f in written:
                row = db.execute('SELECT permalink FROM entity WHERE project_id = ? AND file_path = ?',
                                 (p.project_id, f.rel)).fetchone()
                on_disk, _ = frontmatter_permalink(p.root / f.rel)
                if not row or row[0] != f.new or on_disk != f.new:
                    print(f'    NOT restored: {f.rel} (database {row[0] if row else None}, file {on_disk})')
                    ok = False
            for rel in p.mismatched:
                row = db.execute('SELECT permalink FROM entity WHERE project_id = ? AND file_path = ?',
                                 (p.project_id, rel)).fetchone()
                on_disk, _ = frontmatter_permalink(p.root / rel)
                if not row or row[0] != on_disk:
                    print(f'    NOT realigned: {rel} (database {row[0] if row else None}, file {on_disk})')
                    ok = False
            db.close()
    print('Done.' if ok else 'Done with problems: see above.')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
