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


def parse(fl_bot, keyword):
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
            'Project Url': 'https://www.freelancer.com/projects/' + str(project['id']),
            'Submit Time': time.strftime('%d-%m-%y %H:%M:%S+00:00', time.gmtime(project['time_submitted'])),
            'Expiration Time': time.strftime('%d-%m-%y %H:%M:%S+00:00', time.gmtime(project['time_submitted']+86400*project['bidperiod'])),
            'Active Status': 'Active'
        }


def to_sheets(keyword):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('Creds.json', scope)
    client = gspread.authorize(creds)
    client.import_csv(client.open(keyword).id, open(keyword+'.csv', 'r', encoding='latin1').read())

    return


def main():
    fl_token = ''
    fl_bot = FreelancerBot(fl_token)

    keywords = ['scraping', 'betting']
    dataframes = []

    for keyword in keywords:
        dataframes.append(pd.DataFrame(columns=[
            'Project Id',
            'Title',
            'Description',
            'Minimum Budget',
            'Maximum Budget',
            'Average Bid',
            'Bid Count',
            'Featured',
            'Owner Id',
            'Project Url',
            'Submit Time',
            'Expiration Time',
            'Active Status'
        ]))

    while True:
        try:
            for keyword in range(len(keywords)):
                projects = parse(fl_bot, keywords[keyword])
            
                for project in projects:
                    x = len(dataframes[keyword])
                    dataframes[keyword].loc[x] = project
                    print(dataframes[keyword].loc[x])
                    dataframes[keyword] = dataframes[keyword].drop_duplicates()
            
                for row in range(len(dataframes[keyword])):
                    exp_time = time.mktime(time.strptime(dataframes[keyword].loc[row]['Expiration Time'], '%d-%m-%y %H:%M:%S+00:00'))
                    if time.time() > exp_time:
                        dataframes[keyword].loc[row]['Active Status'] = 'Inactive'

                dataframes[keyword].to_csv(keywords[keyword]+'.csv', index=None)
                to_sheets(keywords[keyword])
            

            time.sleep(3600)

        except Exception as e:
            print(e)
        

if __name__ == '__main__':
    main()
