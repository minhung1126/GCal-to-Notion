import requests


class GCalEvent():
    def __init__(self, info: dict, tz: str) -> None:
        self.info = info
        self.tz = tz


def read_gcal(url) -> list[GCalEvent]:
    rs = requests.Session()

    resp = rs.get(url)
    if not resp.ok:
        # ! warning
        ...

    events = []
    lines = resp.text.splitlines()

    for line in lines:
        if "X-WR-TIMEZONE:" in line:
            tz = line.split(':')[1]

    # If a blank is the first, then it should follow the former line
    to_delete_line_idxs = []
    for idx, line in enumerate(lines):
        if line[0] == " ":
            lines[idx-1] += line[1:]
            to_delete_line_idxs.append(idx)

    for to_delete_line in to_delete_line_idxs[::-1]:
        del lines[to_delete_line]

    while "BEGIN:VEVENT" in lines:
        start_index = lines.index("BEGIN:VEVENT")
        end_index = lines.index("END:VEVENT")
        info = {
            line.split(':')[0].split(';')[0]: ":".join(line.split(':')[1:])
            for line in lines[start_index+1:end_index]
        }
        events.append(GCalEvent(info, tz))
        lines = lines[end_index+1:]

    return events


if __name__ == "__main__":
    pass
