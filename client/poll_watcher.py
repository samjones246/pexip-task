import os
import time
from stat import S_ISDIR
from pathlib import Path
interval = 1
def watch(target : Path, onChange):
    """
    Periodically poll a directory and check for changes. When a change is detected, call onChange
    """
    tree = {}
    while True:
        new_tree = walktree(str(target.absolute().resolve()))
        if tree != None:
            added, removed, changed = detect_changes(tree, new_tree)
            if added or removed or changed:
                onChange(added, removed, changed)
        tree = new_tree
        time.sleep(interval)

def walktree(target):
    """
    Recursively build a tree (as dict) to represent the target directory 
    """
    tree = []
    for f in os.listdir(target):
        path = os.path.join(target, f)
        mode = os.stat(path).st_mode
        if S_ISDIR(mode):
            tree.append((path, "D"))
            tree += walktree(path)
        else:
            tree.append((path, "F"))
    return tree

def detect_changes(old, new):
    """
    Detect changes between two snapshots of a directory tree (old and new)
    Return three dictionaries, containing the files which have been added, removed and changed respectively
    """
    added = []
    removed = []
    changed = []
    for f in old:
        if f not in new:
            removed.append(f)

    for f in new:
        if f not in old:
            added.append(f)
        elif time.time() - os.stat(f[0]).st_mtime <= interval:
            changed.append(f)

    return (added, removed, changed)