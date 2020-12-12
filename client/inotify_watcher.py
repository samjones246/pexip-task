import inotify.adapters
import os
def watch(target, onChange):
    i = inotify.adapters.InotifyTree(target)
    added = []
    removed = []
    changed = []
    for event in i.event_gen():
        if event is None:
            if added or removed or changed:
                onChange(added, removed, changed)
                added = []
                removed = []
                changed = []
            continue
        if 'IN_MODIFY' in event[1]:
            changed.append((os.path.join(event[2], event[3]), 'D' if 'IN_ISDIR' in event[1] else 'F'))
        elif 'IN_CREATE' in event[1]:
            added.append((os.path.join(event[2], event[3]), 'D' if 'IN_ISDIR' in event[1] else 'F'))
        elif 'IN_DELETE' in event[1]:
            removed.append((os.path.join(event[2], event[3]), 'D' if 'IN_ISDIR' in event[1] else 'F'))

if __name__ == "__main__":
    watch("src", print)