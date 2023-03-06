from datetime import datetime

import requests


class NotionElement():
    def texts(texts: str or list) -> list[dict]:
        """Generate text structure for Notion.
        No format included.

        Args:
            texts (strorlist): content

        Returns:
            list[dict]: list of text structure (for rich text especially)
        """
        if type(texts) is str:
            texts = [texts]

        return [
            {
                'type': 'text',
                'text': {'content': text}
            } for text in texts
        ]

    def title(title) -> dict:
        """Generate title for Notion.

        Args:
            title (str): the text of title

        Returns:
            dict: title structure
        """
        return {
            'type': 'title',
            'title': NotionElement.texts(title)
        }

    def divider() -> dict:
        """Generate divider structure for Notion.
        It is a kind of block.

        Returns:
            dict: Divider Structure
        """
        return {
            'type': 'divider',
            'divider': {}
        }

    def date(date: str) -> dict:
        """Generate the date structure for notion

        Args:
            date (str): the date, whether YYYY-MM-DD or isoformat

        Returns:
            dict: date structure
        """
        return {
            'type': 'date',
            'date': {
                'start': date,
            }
        }

    def semester(date: str) -> dict:
        """Generate the semester info automatically for notion

        Args:
            date (str): the date, YYYYMMDD

        Returns:
            dict: semester (select) structure
        """
        time = datetime.strptime(date, "%Y%m%d")
        semester = "2" if 2 <= time.month <= 7 else "1"
        year = time.year-1911 if time.month >= 8 else time.year-1911-1
        return {
            "select": {
                "name": f"{year}-{semester}"
            }
        }


class Notion():
    """A notion object, that can add a page or do something.
    """

    def __init__(self, token: str, db_id: str) -> None:
        self.TOKEN = token
        self.DB_ID = db_id
        self.rs = requests.Session()
        self.rs.headers.update({
            'Authorization': f'Bearer {self.TOKEN}',
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json',
        })
        self.PRESERVE_BLOCK_CONTENT = "".join([
            "Auto generate by 'GCal-to-Notion' service for future use.\n",
            "Use blocks below the divider only.\n",
            "Do NOT use or delete this block.",
        ])

    def search_by_gcal_uid(self, uid: str) -> str:
        """Search the NotionPageID through api, based on GCalUID.

        Args:
            uid (str): GCalUID

        Returns:
            str: NotionPageID
        """
        rs = self.rs
        url = f"https://api.notion.com/v1/databases/{self.DB_ID}/query"

        query = {
            'filter': {
                'property': 'UID',
                'rich_text': {'equals': uid},
            }
        }

        resp = rs.post(
            url,
            json=query
        )

        if not resp.ok:
            # ! ERROR
            ...
        results: list[dict] = resp.json().get('results')
        if results:
            page_id = results[0].get('id', '-1')
        else:
            page_id = "-1"

        return page_id

    def add(
            self,
            uid: str = "",
            name: str = "",
            due: str = "",
            last_modify: str = "",
            description: str = "") -> str:
        """Create a new page in a database.

        Args:
            uid (str, optional): GCalUID. Defaults to "".
            name (str, optional): SUMMARY in GCal. Defaults to "".
            due (str, optional): DTSTART in GCal. Defaults to "".
            last_modify (str, optional): LAST-MODIFY in GCal. Defaults to "".
            description (str, optional): DESCRIPTION in GCal. Defaults to "".

        Returns:
            str: NotionPageID
        """
        rs = self.rs
        url = "https://api.notion.com/v1/pages"

        if description == "":
            first_block = self.PRESERVE_BLOCK_CONTENT
        else:
            first_block = description

        payload = {
            'parent': {
                'type': 'database_id',
                'database_id': self.DB_ID
            },
            'properties': {
                'Name': NotionElement.title(name),
                'Due': NotionElement.date('-'.join([due[0:4], due[4:6], due[6:8]])),
                'Last Modify': NotionElement.date(last_modify),
                'UID': {
                    "rich_text": NotionElement.texts(uid)
                },
                'Semester': NotionElement.semester(due[0:8]),
            },
            'children': [
                {
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': NotionElement.texts(first_block)
                    }
                },
                NotionElement.divider()
            ],
        }

        resp = rs.post(url, json=payload)

        if not resp.ok:
            # ! ERROR
            ...
            return "-1"

        return resp.json().get('id')

    def modify_by_gcal_uid(
            self,
            uid: str = "",
            name: str = "",
            due: str = "",
            last_modify: str = "",
            description: str = "") -> None:
        """Modify page, base on GCalUID.
        If remains blank, then that field won't change

        Args:
            uid (str, optional): GCalUID. Defaults to "".
            name (str, optional): SUMMARY in GCal. Defaults to "".
            due (str, optional): DTSTART in GCal. Defaults to "".
            last_modify (str, optional): LAST-MODIFY in GCal. Defaults to "".
            description (str, optional): DESCRIPTION in GCal. Defaults to "".
        """
        rs = self.rs
        page_id = self.search_by_gcal_uid(uid)
        if page_id == "-1":
            # ! ERROR
            return "-1"
        # Properties
        page_url = f"https://api.notion.com/v1/pages/{page_id}"
        """
        # Get old properties first, then compare
        resp = rs.get(page_url)
        if not resp.ok:
            # ! ERROR
            ...
            return
        page_properties = resp.json().get('properties')

        # Compare, if different, add to payload
        to_update_properties = {}
        if name != "" and name != page_properties['Name']['title'][0]['text']['content']:
            page_properties['Name']['title'][0]['text']['content'] = name
            to_update_properties['Name'] = page_properties['Name']
        if due != "" and due != page_properties['Due']['date']['start']:
            page_properties['Due']['date']['start'] = "-".join(
                [due[0:4], due[4:6], due[6:8]])
            to_update_properties['Due'] = page_properties['Due']
        if last_modify != "" and last_modify != page_properties['Last Modify']['date']['start']:
            page_properties['Last Modify']['date']['start'] = last_modify
            to_update_properties['Last Modify'] = page_properties['Last Modify']
        if uid != "" and uid != page_properties['UID']['rich_text'][0]['text']['content']:
            page_properties['UID']['rich_text'][0]['text']['content'] = uid
            to_update_properties['Last Modify'] = page_properties['Last Modify']
        new_page_data = {
            'properties': to_update_properties
        }
        """
        new_page_data = {
            'properties': {
                'Name': NotionElement.title(name),
                'Due': NotionElement.date('-'.join([due[0:4], due[4:6], due[6:8]])),
                'Last Modify': NotionElement.date(last_modify),
                'UID': {
                    "rich_text": NotionElement.texts(uid)
                },
                'Semester': NotionElement.semester(due[0:8]),
            },
        }
        resp = rs.patch(page_url, json=new_page_data)

        # Blocks
        page_blocks_url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        resp = rs.get(page_blocks_url)
        if not resp.ok:
            # ! ERROR
            ...
            return

        page_blocks = resp.json()
        first_block = page_blocks['results'][0]

        if description == "":
            description = self.PRESERVE_BLOCK_CONTENT

        if first_block['paragraph']['rich_text'] != []:
            first_block_content = first_block['paragraph']['rich_text'][0]['text']['content']
        else:
            first_block_content = ""

        if description != first_block_content:
            block_url = f"https://api.notion.com/v1/blocks/{first_block.get('id')}"
            new_block_content = {
                'paragraph': {
                    'rich_text': NotionElement.texts(description)
                }
            }
            resp = rs.patch(block_url, json=new_block_content)

        return

    def delete_by_gcal_uid(self, uid: str) -> None:
        """Deleta page based on GCalUID

        Args:
            uid (str): GCalUID
        """
        rs = self.rs

        page_id = self.search_by_gcal_uid(uid)
        url = f"https://api.notion.com/v1/pages/{page_id}"

        payload = {
            'archived': True
        }
        resp = rs.patch(url, json=payload)

        if not resp.ok:
            # ! ERROR
            ...

        return None


if __name__ == "__main__":
    pass
