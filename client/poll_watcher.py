import os
import time
from stat import S_ISDIR
from pathlib import Path
interval = 1
def watch(target : Path, onChange):
    """
    Periodically poll a directory and check for changes. When a change is detected, call onChange
    """
    tree = None
    while True:
        new_tree = walktree(str(target.absolute().resolve()))
        if tree != None:
            added, removed, changed = detect_changes(tree, new_tree)
            if added or removed or changed:
                onChange(added, removed, changed)
        tree = new_tree
        time.sleep(interval)

def walktree(target):
    tree = {}
    for f in os.listdir(target):
        path = os.path.join(target, f)
        mode = os.stat(path).st_mode
        if S_ISDIR(mode):
            tree[path] = walktree(path)
        else:
            tree[path] = None
    return tree

def detect_changes(old, new):
    added = {}
    removed = {}
    changed = {}
    for fname, children in old.items():
        if fname not in new:
            removed[fname] = children

    for fname, children in new.items():
        if fname not in old:
            added[fname] = children
        else:
            if children is not None:
                added_c, removed_c, changed_c = detect_changes(old[fname], children)
                added.update(added_c)
                removed.update(removed_c)
                changed.update(changed_c)
            elif time.time() - os.stat(fname).st_mtime <= interval:
                changed[fname] = children
    
    return (added, removed, changed)