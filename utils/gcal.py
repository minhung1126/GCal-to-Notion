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

    while "BEGIN:VEVENT" in lines:
        start_index = lines.index("BEGIN:VEVENT")
        end_index = lines.index("END:VEVENT")
        info = {
            line.split(':')[0].split(';')[0]: line.split(':')[1]
            for line in lines[start_index+1:end_index]
        }
        events.append(GCalEvent(info, tz))
        lines = lines[end_index+1:]

    return events


if __name__ == "__main__":
    pass
