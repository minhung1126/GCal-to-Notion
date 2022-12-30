import sys
from datetime import datetime
import logging

from utils import gcal
from utils.notion import Notion
from utils.history import History
"""TESTMESSAGE"""

def set_logging():
    main_logger = logging.getLogger()
    main_logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '[%(asctime)s][%(levelname)s]%(module)s.%(funcName)s.L%(lineno)03d: %(message)s',
        datefmt='%Y-%m-%d %H-%M-%S')

    stream_logger = logging.StreamHandler()
    stream_logger.setFormatter(formatter)

    main_logger.handlers.clear()
    main_logger.handlers.append(stream_logger)

    return


def main():
    gcal_url, notion_token, notion_db_id = sys.argv[1:]
    logging.info('GcalUrl, NotionToken, NotionDBID get')
    logging.debug(f'GcalUrl: *****{gcal_url[:-10]}')
    logging.debug(f'NotionToken: {notion_token[:10]}*****')
    logging.debug(f'NotionDBID: {notion_db_id[:5]}*****')

    global history, notion
    history = History()
    notion = Notion(notion_token, notion_db_id)

    events = gcal.read_gcal(gcal_url)
    logging.info(f"Get {len(events)} events from remote")

    # Add or Modify
    for event in events:
        logging.info(f'Comparing: {event}')
        if not history.is_gcal_uid_in_history(event.uid):
            logging.info(f'New event {event} found on google calander')
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
                logging.info(f'Successfully add to notion ({notion_page_id})')
                history.add({
                    'GCalUID': event.uid,
                    'NotionPageID': notion_page_id,
                    'LastModify': event.last_modify,
                })
        elif datetime.strptime(event.last_modify, "%Y%m%dT%H%M%SZ") > \
            datetime.strptime(
                history.search_by_gcal_uid(event.uid).get('LastModify'),
                "%Y%m%dT%H%M%SZ"):
            logging.info(f"{event} is modified on google calander")
            notion.modify_by_gcal_uid(
                uid=event.uid,
                name=event.name,
                due=event.due,
                last_modify=event.last_modify,
                description=event.description
            )
            logging.info(f'Successfully modify {event}')
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
        logging.info(f"{event} is deleted on google calander.")
        notion.delete_by_gcal_uid(to_delete_uid)
        logging.info(f"Successfully delete {event} on notion")
        history.delete_by_uid(to_delete_uid)

    return


if __name__ == "__main__":
    main()
