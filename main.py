import os
import sys
from notion_client import Client
import things
import webbrowser
import pandas as pd
import datetime
import json

def main():
    if not os.path.isfile('config.json'): # check to see if config exists
        print("Error: Run config.py, no config found.")
        sys.exit(0)

    with open("config.json", "r") as jsonfile: # read config
            data = json.load(jsonfile)

    # user defaults
    token = data['token']
    database = data['database']
    notion = Client(auth=token)

    if not os.path.isfile('data.csv'): # check to see if data path exists
        df = pd.DataFrame(columns=['id', 'name', 'date', 'tag'])
        df.to_csv('data.csv', index=False)

    df = pd.read_csv('data.csv')
    x = len(df)
    today = datetime.datetime.today().date()

    database = notion.databases.query(
        **{
            "database_id": database,
        }
    )

    projects = [x['title'] for x in things.projects()]

    for entry in database['results']:
        properties =  entry['properties']
        id = str(entry['id'])

        if id not in df['id'].values: # if new entry
            try:
                date = properties['Date']['date']['start']
                date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
                progress = properties['Progress']['select']['name']
                name = properties['Name']['title'][0]['plain_text']
                tag = properties['Tags']['multi_select'][0]['name']
                if tag not in projects:
                    webbrowser.open('things:///add-project?title='+tag+'&area=Berkeley')
                    projects = [x['title'] for x in things.projects()]
            except:
                date = None
                progress = None
            if (progress == "Not Started") and not (date < today): # things needs todos today or later
                df.loc[x] = [id, name, date, tag]
                webbrowser.open('things:///add?title='+name+'&notes='+id+'&when='+date.strftime('%Y-%m-%d')+'&list='+tag) # add to things
                x += 1
            elif (progress == "Completed") and not (date < today): # got marked as completed but not in things
                df.loc[x] = [id, name, date, tag]
                notion.pages.update(id, properties={
                    'Progress': {'id': 'y%40%5DD',
                       'type': 'select',
                       'select': {'id': '33e9a473-dfc9-4531-8359-5d9bd10e2745',
                            'name': 'Not Started',
                            'color': 'red'}
                    }
                })
                x += 1
        else: # otherwise check to see if completed
            in_todo = False
            for todo in things.todos():
                if todo['notes'] == id:
                    in_todo = True
            if not in_todo: # if things marked as completed, delete and update notion
                notion.pages.update(id, properties={
                    'Progress': {'id': 'y%40%5DD',
                        'type': 'select',
                        'select': {'id': '5bde3130-3aa9-4d8b-993d-6a15051f3e2a',
                            'name': 'Completed',
                            'color': 'green'},
                    }
                })
                df = df[~df['id'].isin([id])]
                df = df.reset_index(drop=True)

    df.to_csv('data.csv', index=False)
if __name__ == "__main__":
    main()
