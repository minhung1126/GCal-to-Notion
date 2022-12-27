import sys
from datetime import datetime

from utils import gcal
from utils.gcal import GCalEvent
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
        gcal_uid = event.info.get('UID')
        name = event.info.get('SUMMARY')
        due = event.info.get('DTSTART')
        last_modify = event.info.get('LAST-MODIFIED')
        description = event.info.get('DESCRIPTION')
        if not history.is_gcal_uid_in_history(gcal_uid):
            notion_page_id = notion.add(
                uid=gcal_uid,
                name=name,
                due=due,
                last_modify=last_modify,
                description=description
            )
            history.add({
                'GCalUID': gcal_uid,
                'NotionPageID': notion_page_id,
                'LastModify': last_modify,
            })
        elif datetime.fromisoformat(last_modify) > \
            datetime.fromisoformat(
                history.search_by_gcal_uid(gcal_uid).get('LastModify')
        ):
            notion.modify_by_uid(
                uid=gcal_uid,
                name=name,
                due=due,
                last_modify=last_modify,
                description=description
            )
            history.modify({
                'GCalUID': gcal_uid,
                'LastModify': last_modify,
            })
    # Delete events that is delete on gcal
    gcal_event_uids = set([
        event.info.get('GCalUID') for event in events
    ])
    uids_in_history = set(history.all_gcal_uids())

    for to_delete_uid in uids_in_history-gcal_event_uids:
        notion.delete_by_uid(to_delete_uid)
        history.delete_by_uid(gcal_uid)

    return


if __name__ == "__main__":
    main()
