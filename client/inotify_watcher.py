import inotify.adapters
import os
def watch(target, onChange, ignore_hidden):
    i = inotify.adapters.InotifyTree(str(target))
    updates = []
    renames = []
    utypes = {
        'IN_CREATE': 'A',
        'IN_MODIFY': 'C',
        'IN_DELETE': 'R',
        'IN_MOVED_FROM':'MF',
        'IN_MOVED_TO': 'MT'
    }
    for event in i.event_gen():
        if event is None:
            cookies = {}
            for event in renames:
                if event[3] in cookies:
                    if cookies[event[3]][0] == "MF":
                        updates.append(('M', (cookies[event[3]][1], event[1]), event[2]))
                    else:
                        updates.append(('M', (event[1], cookies[event[3]][1]), event[2]))
                    cookies.pop(event[3])
                else:
                    cookies[event[3]] = event
            for event in cookies.values():
                if event[0] == "MF":
                    updates.append(("R", event[1], event[2]))
                else:
                    updates.append(("A", event[1], event[2]))
            if updates:
                onChange(updates)
                updates = []
                renames = []
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
                if utype in ["MF", "MT"]:
                    renames.append((utype, fpath, ftype, event[0].cookie))
                else:
                    updates.append((utype, fpath, ftype))

if __name__ == "__main__":
    watch("src", print, True)