#!/usr/bin/env python3
"""Reindex basic-memory projects, one run at a time on this machine.

The plugin's MCP server runs with BASIC_MEMORY_SYNC_CHANGES=false (.mcp.json):
with one server per open session, every server's file watcher synced the same
file at once, which produced duplicate "-1" permalinks and failed frontmatter
writes. Memory files are indexed through this script instead:

  (no arguments)        PostToolUse hook for Write/Edit: when the file lies in
                        a registered basic-memory project, start a detached
                        reindex of that project and return at once.
  --all                 SessionStart hook: start a detached reindex of every
                        project, the catch-up each MCP server used to run at
                        startup (edits made outside Claude Code, other accounts).
  --path PATH           Reindex the project containing PATH in the foreground
                        and print its `basic-memory status` (commands); the
                        option can be repeated.
  --background          The detached run started by the two hooks.

Every run takes one lock shared by all sessions and accounts. A detached run
that finds another one already waiting for the same project exits: the waiting
run starts after the current one and sees its changes.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import time
from typing import IO

BM = os.environ.get('PM_BASIC_MEMORY_BIN', 'basic-memory')
# Multi-account aware, like the other hooks: wrapper aliases (e.g. `claude-work`)
# set BASIC_MEMORY_CONFIG_DIR to isolate per-account state.
BM_CONFIG_DIR = os.path.expanduser(os.environ.get('BASIC_MEMORY_CONFIG_DIR') or '~/.basic-memory')
BM_CONFIG = os.path.join(BM_CONFIG_DIR, 'config.json')
BM_DB = os.path.join(BM_CONFIG_DIR, 'memory.db')
# Machine-wide rather than per config dir: two accounts with separate databases
# can register the same folder (the shared global layer), and two runs that
# rewrite the same file's frontmatter at once make one of the writes fail.
LOCK_DIR = os.path.join(os.path.expanduser(os.environ.get('XDG_CACHE_HOME') or '~/.cache'), 'persistmind')
RUN_LOCK = os.path.join(LOCK_DIR, 'reindex.lock')
# A command waits on a foreground run, so it gives up sooner than a detached one.
FOREGROUND_WAIT_S = 90.0
BACKGROUND_WAIT_S = 600.0
REINDEX_TIMEOUT_S = 300.0
POLL_S = 0.2


def load_projects() -> dict[str, str]:
    """Registered basic-memory projects with a local path: name -> real path."""
    try:
        with open(BM_CONFIG) as f:
            cfg = json.load(f)
    except Exception:
        return {}
    projects: dict[str, str] = {}
    for name, entry in (cfg.get('projects') or {}).items():
        path = entry.get('path') if isinstance(entry, dict) else entry
        if isinstance(path, str) and os.path.isabs(os.path.expanduser(path)):
            projects[name] = os.path.realpath(os.path.expanduser(path))
    return projects


def project_for(path: str, projects: dict[str, str]) -> str | None:
    """The project containing `path` (the deepest one if roots nest), or None
    when the path is outside every project or hidden inside one: basic-memory
    skips dotfiles and dot-directories."""
    target = os.path.realpath(os.path.expanduser(path))
    best: tuple[str, str] | None = None
    for name, root in projects.items():
        inside = target == root or target.startswith(root.rstrip(os.sep) + os.sep)
        if inside and (best is None or len(root) > len(best[1])):
            best = (name, root)
    if best is None:
        return None
    rel = os.path.relpath(target, best[1])
    if any(part.startswith('.') for part in rel.split(os.sep) if part != '.'):
        return None
    return best[0]


def acquire(path: str, wait_s: float) -> IO[str] | None:
    """Take an exclusive lock on `path`, retrying for up to `wait_s` seconds.
    The lock lives as long as the returned handle; the OS drops it if the
    process dies, so a crashed run never leaves a stale lock."""
    os.makedirs(LOCK_DIR, exist_ok=True)
    handle = open(path, 'a')
    deadline = time.monotonic() + wait_s
    while True:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return handle
        except BlockingIOError:
            if time.monotonic() >= deadline:
                handle.close()
                return None
            time.sleep(POLL_S)


def queue_lock_path(project: str | None) -> str:
    """One waiting slot per project of this basic-memory database."""
    key = f"{os.path.realpath(BM_CONFIG_DIR)}\0{project or '*'}"
    return os.path.join(LOCK_DIR, f'queue-{hashlib.sha256(key.encode()).hexdigest()[:16]}.lock')


def rewind_watermark(project: str | None) -> None:
    """Work around basic-memory's incremental scan on macOS. It lists changed
    files with `find -newermt <start of the previous sync, cut to the second>`
    and BSD find compares whole seconds, so a file written in the same second
    as the previous sync's start, but after it, is skipped by every later
    scan. Moving the watermark back to the previous whole second makes the
    scan look at that second again; files already indexed there are
    recognised as unchanged by their mtime and size."""
    if not os.path.isfile(BM_DB):
        return
    sql = ('UPDATE project SET last_scan_timestamp = CAST(last_scan_timestamp AS INTEGER) - 1 '
           'WHERE last_scan_timestamp IS NOT NULL')
    try:
        con = sqlite3.connect(BM_DB, timeout=10)
        try:
            with con:
                if project:
                    con.execute(sql + ' AND name = ?', (project,))
                else:
                    con.execute(sql)
        finally:
            con.close()
    except sqlite3.Error:
        pass  # schema changed or database busy: the scan just runs as before


def reindex(project: str | None, capture: bool) -> tuple[int, str]:
    """Run `basic-memory reindex` (incremental) for one project, or all."""
    rewind_watermark(project)
    cmd = [BM, 'reindex'] + (['--project', project] if project else [])
    out = subprocess.PIPE if capture else subprocess.DEVNULL
    err = subprocess.STDOUT if capture else subprocess.DEVNULL
    try:
        proc = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                              text=True, timeout=REINDEX_TIMEOUT_S)
    except FileNotFoundError:
        return 127, f'{BM}: command not found'
    except subprocess.TimeoutExpired:
        return 124, f'reindex timed out after {REINDEX_TIMEOUT_S:.0f} s'
    return proc.returncode, proc.stdout or ''


def spawn_background(project: str | None) -> None:
    """Start a detached run (all projects when `project` is None). It gets its
    own session and no inherited pipes, so the calling hook returns at once
    and the run survives the hook's exit."""
    target = ['--project', project] if project else ['--all']
    try:
        subprocess.Popen([sys.executable, os.path.abspath(__file__), '--background', *target],
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True, close_fds=True)
    except OSError:
        pass


def spawn_for_path(path: str) -> None:
    """Start a detached reindex of the project containing `path`, if any."""
    name = project_for(path, load_projects())
    if name is not None:
        spawn_background(name)


def run_background(project: str | None) -> int:
    queued = acquire(queue_lock_path(project), 0)
    if queued is None:
        return 0  # another run waits for this project and will see our change
    try:
        lock = acquire(RUN_LOCK, BACKGROUND_WAIT_S)
    finally:
        # Free the waiting slot before scanning: a change made from now on
        # must queue a new run, since this scan may already have passed it.
        queued.close()
    if lock is None:
        return 1
    try:
        return reindex(project, capture=False)[0]
    finally:
        lock.close()


def run_foreground(paths: list[str]) -> int:
    projects = load_projects()
    names: list[str] = []
    rc = 0
    for path in paths:
        name = project_for(path, projects)
        if name is None:
            print(f'Not in a registered basic-memory project: {path}')
            rc = 1
        elif name not in names:
            names.append(name)
    for name in names:
        lock = acquire(RUN_LOCK, FOREGROUND_WAIT_S)
        if lock is None:
            print(f'{name}: another reindex was still running after {FOREGROUND_WAIT_S:.0f} s; retry later.')
            rc = 1
            continue
        started = time.monotonic()
        try:
            code, output = reindex(name, capture=True)
        finally:
            lock.close()
        if code != 0:
            tail = '\n'.join(output.strip().splitlines()[-10:])
            print(f'{name}: reindex failed (exit {code})\n{tail}')
            rc = 1
            continue
        print(f'{name}: reindexed in {time.monotonic() - started:.1f} s')
        status = subprocess.run([BM, 'status', '--project', name], stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        print(status.stdout.strip())
    return rc


def run_hook() -> int:
    """PostToolUse: never fails the tool call, whatever happens."""
    try:
        data = json.loads(sys.stdin.read())
        file_path = (data.get('tool_input') or {}).get('file_path') or ''
        if file_path:
            spawn_for_path(file_path)
    except Exception:
        pass
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Reindex basic-memory projects, one run at a time.')
    parser.add_argument('--path', action='append', default=[], help='reindex the project containing PATH')
    parser.add_argument('--all', action='store_true', help='start a detached reindex of every project')
    parser.add_argument('--project', help=argparse.SUPPRESS)
    parser.add_argument('--background', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.background:
        return run_background(None if args.all else args.project)
    if args.all:
        spawn_background(None)
        return 0
    if args.path:
        return run_foreground(args.path)
    return run_hook()


if __name__ == '__main__':
    sys.exit(main())
