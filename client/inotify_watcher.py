import inotify.adapters
import os
def watch(target, onChange, ignore_hidden):
    i = inotify.adapters.InotifyTree(str(target))
    updates = []
    utypes = {
        'IN_CREATE': 'A',
        'IN_MODIFY': 'C',
        'IN_DELETE': 'R'
    }
    for event in i.event_gen():
        if event is None:
            if updates:
                onChange(updates)
                updates = []
            continue
        if event[1][0] in utypes:
            utype = utypes[event[1][0]]
            fpath = os.path.join(event[2], event[3])
            ignore = False
            if ignore_hidden:
                parts = os.path.relpath(fpath, target).split("/")
                for part in parts:
                    if part.startswith("."):
                        ignore = True
            if not ignore:
                ftype = 'D' if 'IN_ISDIR' in event[1] else 'F'
                updates.append((utype, fpath, ftype))

if __name__ == "__main__":
    watch("src", print)