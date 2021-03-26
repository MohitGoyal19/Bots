# -*- coding: utf-8 -*-

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import requests
import time

class FreelancerBot():
    token = ''
    url = 'https://www.freelancer.com/api/projects/0.1/projects/active/'
    headers = ''

    def __init__(self, token):
        self.token = token
        self.headers = {'freelancer-oauth-v1': self.token}

    def get_projects(self, query, count=10):
        epoch_time = int(time.time()) - 86400
        url = self.url + '?query={}'.format(query)
        projects = requests.get(url, headers=self.headers).json()['result']['projects']
        
        return projects


class TelegramBot():
    token = ''
    url = 'https://api.telegram.org/bot'
    update_id = None
    keywords = []
    
    def __init__(self, token):
        self.token = token
        self.url = self.url + token


    def get_updates(self, timeout=None):
        url = self.url + '/getUpdates?offset={}&timeout={}'.format(self.update_id, timeout)
        print(requests.get(url).json())

        return requests.get(url).json()


    def parse(self, updates, fl_bot):
        for update in updates['result']:
            self.update_id = update['update_id'] + 1
            in_message = update['edited_message']['text'] if 'edited_message' in update.keys() else update['message']['text']
            if '/' == in_message[0]:
                continue
            
            self.keywords.append(in_message)
        print(self.keywords)

        for keyword in self.keywords:
            projects = fl_bot.get_projects(keyword)
            for project in projects:    
                yield {
                    'Project Id': project['id'],
                    'Title': project['title'],
                    'Description': project['preview_description'] if project['preview_description'] else '',
                    'Minimum Budget': str(project['budget']['minimum']) + ' ' + project['currency']['code'] ,
                    'Maximum Budget': str(project['budget']['maximum']) + ' ' + project['currency']['code'],
                    'Average Bid': str(project['bid_stats']['bid_avg']) + ' ' + project['currency']['code'],
                    'Bid Count': project['bid_stats']['bid_count'],
                    'Featured': 'Yes' if project['featured'] else 'No',
                    'Owner Id': project['owner_id'],
                    'Project Url': 'https://www.freelancer.com/projects/' + str(project['id'])
                }


def to_sheets():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('Creds.json', scope)
    client = gspread.authorize(creds)
    client.import_csv(client.open('Freelancer').id, open('freelancer.csv', 'r', encoding='latin1').read())

    return


def main():
    fl_token = ''
    fl_bot = FreelancerBot(fl_token)

    tg_token = ''
    tg_bot = TelegramBot(tg_token)

    output = pd.DataFrame(columns=[
        'Project Id',
        'Title',
        'Description',
        'Minimum Budget',
        'Maximum Budget',
        'Average Bid',
        'Bid Count',
        'Featured',
        'Owner Id',
        'Project Url'
    ])

    while True:
        for i in ['true']:
            updates = tg_bot.get_updates(60)
            projects = tg_bot.parse(updates, fl_bot)
            for project in projects:
                x = len(output)
                output.loc[x] = project
                print(output.loc[x])
                output = output.drop_duplicates()
            output.to_csv('freelancer.csv', index=None)
            to_sheets()
        

if __name__ == '__main__':
    main()
