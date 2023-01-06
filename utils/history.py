import os
import csv


class History():
    """A history object for monitering.
    As a csv format, shown in below:
        GCalUID,NotionPageID,LastModify
        ...    ,...         ,...
    Note that it is 'GCalUID' based.
    """

    def __init__(self) -> None:
        self.FIELDNAMES = ['GCalUID', 'NotionPageID', 'LastModify']
        self.FILE_PATH = os.path.join('.', 'history.csv')
        if not os.path.isfile(self.FILE_PATH):
            with open(self.FILE_PATH, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
                writer.writeheader()
            self.history = []
        else:
            with open(self.FILE_PATH, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                self.history = [row for row in reader]

    def _save_history(self) -> None:
        """Save history
        """
        # Make back up
        os.rename(self.FILE_PATH, self.FILE_PATH+".bak")

        # Write new file
        with open(self.FILE_PATH, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
            writer.writeheader()

            writer.writerows(self.history)

        # Delete Backup
        os.remove(self.FILE_PATH+".bak")
        return

    def add(self, info: dict) -> None:
        """Add a event to history.

        Args:
            info (dict): The event info. Should include keys as below: 
                {
                    "GCalUID": ...,
                    "NotionPageID": ...,
                    "LastModify": ...,
                }
        """
        self.history.append(info)
        self._save_history()
        return

    def modify(self, info: dict) -> None:
        """Modify the info of the given GCalUID

        Args:
            info (dict): The event info. Should include keys as below: 
                {
                    "GCalUID": ...,
                    "NotionPageID": ...,
                    "LastModify": ...,
                }
        """
        for history in self.history:
            if history.get('GCalUID') == info.get('GCalUID'):
                history.update(info)
                break

        self._save_history()
        return

    def delete_by_uid(self, uid: str):
        """Delete the event info based on the GCalUID.

        Args:
            uid (str): GCalUID
        """
        self.history = list(filter(
            lambda x: x['GCalUID'] != uid,
            self.history
        ))

        self._save_history()
        return

    def all_gcal_uids(self) -> list[str]:
        """Get all GCalUID in history

        Returns:
            list[str]: list of GCalUID
        """
        return [
            history.get('GCalUID')
            for history in self.history
        ]

    def is_gcal_uid_in_history(self, gcal_uid: str) -> bool:
        """Whether the GCalUID is in history

        Args:
            gcal_uid (str): GCalUID

        Returns:
            bool: GCalUID is in history or not
        """
        return bool(list(filter(
            lambda x: gcal_uid == x.get('GCalUID', ''),
            self.history
        )))

    def is_notion_page_id_in_history(self, notion_page_id: str) -> bool:
        """Whether the NotionPageID is in history

        Args:
            notion_page_id (str): NotionPageID

        Returns:
            bool: NotionPageID is in history or not
        """
        return bool(list(filter(
            lambda x: notion_page_id == x.get('NotionPageID', ''),
            self.history
        )))

    def search_by_gcal_uid(self, gcal_uid: str) -> dict:
        """Search the info of the given GCalUID

        Args:
            gcal_uid (str): GCalUID

        Returns:
            dict: dict of info of that event. {} if not found.
        """
        if self.is_gcal_uid_in_history(gcal_uid):
            return list(filter(
                lambda x: gcal_uid == x.get('GCalUID', ''),
                self.history
            ))[0]
        else:
            return {}

    def search_by_notion_page_id(self, notion_page_id: str):
        """Search the info of the given NotionPageID

        Args:
            gcal_uid (str): NotionPageID

        Returns:
            dict: dict of info of that event. {} if not found.
        """
        if self.is_notion_page_id_in_history(notion_page_id):
            return list(filter(
                lambda x: notion_page_id == x.get('NotionPageID', '')
            ))[0]
        else:
            return {}


if __name__ == "__main__":
    pass
