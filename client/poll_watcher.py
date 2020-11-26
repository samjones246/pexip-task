import os
import time
from pathlib import Path

def watch(target : Path, onChange):
    interval = 1
    """
    Periodically poll a directory and check for changes. When a change is detected, call onChange
    """
    tree = None
    while True:
        new_tree = dict([(f.name, f) for f in os.scandir(str(target))])
        if tree != None:
            added, removed, changed = detect_changes(tree, new_tree)
            if added or removed:
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
    
    return (added, removed, changed)