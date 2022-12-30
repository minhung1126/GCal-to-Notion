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

    def title(title):
        return {
            'type': 'title',
            'title': NotionElement.texts(title)
        }

    def divider() -> dict:
        """Generate divider structure for Notion
        It is a kind of block

        Returns:
            dict: Divider Structure
        """
        return {
            'type': 'divider',
            'divider': {}
        }

    def date(date) -> dict:
        return {
            'type': 'date',
            'date': {
                'start': date,
            }
        }


class Notion():
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

    def search_by_gcal_uid(self, uid) -> str:
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
            description: str = "") -> str:
        rs = self.rs
        page_id = self.search_by_gcal_uid(uid)
        if page_id == "-1":
            # ! ERROR
            return "-1"

        # Properties
        page_url = f"https://api.notion.com/v1/pages/{page_id}"
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
            page_properties['Due']['date']['start'] = "-".join([due[0:4],due[4:6],due[6:8]])
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

    def delete_by_gcal_uid(self, uid) -> str:
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
