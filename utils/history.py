import os
import csv


class History():
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

    def add(self, info: dict):
        self.history.append(info)
        self._save_history()
        return

    def is_gcal_uid_in_history(self, gcal_uid) -> bool:
        return bool(list(filter(
            lambda x: gcal_uid == x.get('GCalUID', ''),
            self.history
        )))

    def is_notion_page_id_in_history(self, notion_page_id) -> bool:
        return bool(list(filter(
            lambda x: notion_page_id == x.get('NotionPageID', ''),
            self.history
        )))

    def search_by_gcal_uid(self, gcal_uid) -> dict:
        if self.is_gcal_uid_in_history(gcal_uid):
            return list(filter(
                lambda x: gcal_uid == x.get('GCalUID', '')
            ))[0]
        else:
            return {}

    def search_by_notion_page_id(self, notion_page_id):
        if self.is_notion_page_id_in_history(notion_page_id):
            return list(filter(
                lambda x: notion_page_id == x.get('NotionPageID', '')
            ))[0]
        else:
            return {}


if __name__ == "__main__":
    pass
