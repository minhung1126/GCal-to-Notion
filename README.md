# GCal-to-Notion
Tool to copy the events' information in Google Calender to Notion Database.  
Create, modify, selete supported.

## Setting up

### Notion api

1. Visit the api integrations page ([here](https://www.notion.so/my-integrations)).
2. Create a new integration, and remember the **TOKEN**.
3. Create a new database, and click **Add connection**, and choose your integrations created beforehand. Remember the **Database ID** (End of the url).
4. Click **Properties** of the database, make sure you have the following properties with correct type.  

|Property Name|Type|
|---|---|
|Name|`Title`|
|Due|`Date`|
|UID|`Text`|
|Last Modify|`Date`|
|Semester|`Select`|

### Google Calender

1.  Go to setting, select the calendar you want.
2.  Copy the **private url**, which ends with **.ics**.
3.  Remember the url.

### Github

1. Create a personal access tokens. Remember this **TOKEN**.
2. Open Repo > Settings > Secrets > Actions.
3. Click **New repository secret**, and add TOKENs as below.

|TOKEN name|TOKEN content|
|---|---|
|`GCALURL`|The Google Calender private url.|
|`GH_TOKEN`|The GitHub personal access tokens.|
|`NOTION_DB_ID`|The Notion datebase id.|
|`NOTION_TOKEN`|The Notion intergration secret TOKEN.|

## Modify
You can edit the workflow file to adjust the frequency.  
You can start the workflow manually on Action page. (defult)
