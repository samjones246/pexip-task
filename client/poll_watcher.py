import os
import time
from pathlib import Path
interval = 1
def watch(target : Path, onChange):
    """
    Periodically poll a directory and check for changes. When a change is detected, call onChange
    """
    tree = None
    while True:
        new_tree = dict([(f.name, f) for f in os.scandir(str(target))])
        if tree != None:
            added, removed, changed = detect_changes(tree, new_tree)
            if added or removed or changed:
                onChange(added, removed, changed)
        tree = new_tree
        time.sleep(interval)

def detect_changes(old : dict, new : dict):
    added = []
    removed = []
    changed = []
    for fname, f in old.items():
        if fname not in new:
            removed.append(fname)

    for fname, f in new.items():
        if fname not in old:
            added.append(fname)
        else:
            if time.time() - os.stat(f.path).st_mtime <= interval:
                changed.append(fname)
    
    return (added, removed, changed)