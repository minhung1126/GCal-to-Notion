import os
import time
import requests


class GCalEvent():
    """A Google-Calender (GCal) Object
    """

    def __init__(self, info: dict) -> None:
        """Create a GCalEvent

        Args:
            info (dict): including:
                UID,
                SUMMARY (as name, use for title),
                DTSTART (as due, use for due date),
                LAST-MODIFIED (as last_modify, use for version check),
                DESCRIPTION (as description, use for page's first block content)
        """
        self.info = info

        self.uid: str = info.get('UID')
        self.name: str = info.get('SUMMARY')
        self.due: str = info.get('DTSTART')
        self.last_modify: str = info.get('LAST-MODIFIED')
        self.description: str = info.get('DESCRIPTION', '')

    def __str__(self):
        return f"{self.name}({self.uid})"


class GCalReadFail(Exception):
    """Fail to read gcal"""


def read_gcal(url: str) -> list[GCalEvent]:
    """Get all events from GCal.
    Requests the url first, then parse to generate info dict.
    Create a GCalEvent object, and return them all in a list

    Args:
        url (str): url of the calender

    Returns:
        list[GCalEvent]: list of GCalEvent object
    """
    rs = requests.Session()

    for i in range(30):
        try:
            resp = rs.get(url)
        except requests.RequestException:
            # Do nothing
            time.sleep(10)
            continue

        if not resp.ok:
            continue

        if "<!doctype html>" in resp.text:
            continue

        break
    else:
        raise GCalReadFail

    events = []
    lines = resp.text.splitlines()

    # for line in lines:
    #     if "X-WR-TIMEZONE:" in line:
    #         tz = line.split(':')[1]

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
            line.split(':')[0].split(';')[0]: ":".join(
                line.split(':')[1:]).replace('\\n', '\n')
            for line in lines[start_index+1:end_index]
        }
        events.append(GCalEvent(info))
        lines = lines[end_index+1:]

    return events


if __name__ == "__main__":
    pass
