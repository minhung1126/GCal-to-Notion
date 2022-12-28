import sys
from datetime import datetime

from utils import gcal
from utils.notion import Notion
from utils.history import History


def main():
    gcal_url, notion_token, notion_db_id = sys.argv[1:]

    global history, notion
    history = History()
    notion = Notion(notion_token, notion_db_id)

    events = gcal.read_gcal(gcal_url)

    # Add or Modify
    for event in events:
        if not history.is_gcal_uid_in_history(event.uid):
            notion_page_id = notion.add(
                uid=event.uid,
                name=event.name,
                due=event.due,
                last_modify=event.last_modify,
                description=event.description
            )
            history.add({
                'GCalUID': event.uid,
                'NotionPageID': notion_page_id,
                'LastModify': event.last_modify,
            })
        elif datetime.strptime(event.last_modify, "%Y%m%dT%H%M%SZ") > \
            datetime.strptime(
                history.search_by_gcal_uid(event.uid).get('LastModify'),
                "%Y%m%dT%H%M%SZ"
        ):
            notion.modify_by_uid(
                uid=event.uid,
                name=event.name,
                due=event.due,
                last_modify=event.last_modify,
                description=event.description
            )
            history.modify({
                'GCalUID': event.uid,
                'LastModify': event.last_modify,
            })

    # Delete events that is deleted on gcal
    gcal_event_uids = set([
        event.uid for event in events
    ])
    uids_in_history = set(history.all_gcal_uids())

    for to_delete_uid in uids_in_history-gcal_event_uids:
        notion.delete_by_uid(to_delete_uid)
        history.delete_by_uid(to_delete_uid)

    return


if __name__ == "__main__":
    main()
