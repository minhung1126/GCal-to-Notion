import sys
from datetime import datetime
import logging

from utils import gcal
from utils.notion import Notion
from utils.history import History


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    history_formatter = logging.Formatter(
        '[%(asctime)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_hdlr = logging.FileHandler(
        'Worklog.txt', 'a', encoding='utf-8'
    )
    file_hdlr.setFormatter(history_formatter)
    file_hdlr.setLevel(logging.DEBUG)
    logger.addHandler(file_hdlr)

    return


def main():
    setup_logging()
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
            if notion_page_id == "-1":
                #! Fail
                ...
            else:
                history.add({
                    'GCalUID': event.uid,
                    'NotionPageID': notion_page_id,
                    'LastModify': event.last_modify,
                })
                logging.debug(f'Add: {event.uid} -> {notion_page_id}')
        elif datetime.strptime(event.last_modify, "%Y%m%dT%H%M%SZ") > \
            datetime.strptime(
                history.search_by_gcal_uid(event.uid).get('LastModify'),
                "%Y%m%dT%H%M%SZ"):
            notion.modify_by_gcal_uid(
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
            logging.debug(f'Modify: {event.uid}')

    # Delete events that is deleted on gcal
    gcal_event_uids = set([
        event.uid for event in events
    ])
    uids_in_history = set(history.all_gcal_uids())

    for to_delete_uid in uids_in_history-gcal_event_uids:
        notion.delete_by_gcal_uid(to_delete_uid)
        history.delete_by_gcal_uid(to_delete_uid)
        logging.debug(f'Delete: {to_delete_uid}')

    return


if __name__ == "__main__":
    main()
