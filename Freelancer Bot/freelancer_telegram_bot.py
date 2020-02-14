# -*-coding: utf-8-*-

import requests

class FreelancerBot():
    token = ''
    url = 'https://www.freelancer.com/api/projects/0.1/projects/all/'
    headers = ''

    def __init__(self, token):
        self.token = token
        self.headers = {'freelancer-oauth-v1': self.token}

    def get_projects(self, query, count=10):
        url = self.url + '?query={}&count={}'.format(query, count)
        projects = requests.get(url, headers=self.headers).json()['result']['projects']
        project_urls = ['https://www.freelancer.com/projects/' + project['seo_url'] for project in projects]

        return project_urls


class TelegramBot():
    token = ''
    url = 'https://api.telegram.org/bot'
    update_id = None
    
    def __init__(self, token):
        self.token = token
        self.url = self.url + token

    def get_updates(self, timeout=None):
        url = self.url + '/getUpdates?offset={}&timeout={}'.format(self.update_id, timeout)

        return requests.get(url).json()

    def send_message(self, chat_id, message):
        url = self.url + '/sendMessage?chat_id={}&text={}'.format(chat_id, message)
        requests.get(url)

        return

    def parse(self, updates, fl_bot):
        for update in updates['result']:
            self.update_id = update['update_id']
            in_message = update['message']['text']
            if '/' == in_message[0]:
                return

            chat_id = update['message']['chat']['id']
            projects = fl_bot.get_projects(in_message)
            for out_message in projects:    
                self.send_message(chat_id, out_message)

        return


def main():
    fl_token = 'ft0V3ui5QSMXbEQzRi8dDXCWtnBCcu'
    fl_bot = FreelancerBot(fl_token)

    tg_token = '1028458800:AAGwFb8FXj52fwD0wFsPdnOoLT2nBO4qnqg'
    tg_bot = TelegramBot(tg_token)
    while True:
        updates = tg_bot.get_updates(60)
        tg_bot.parse(updates, fl_bot)

if __name__ == '__main__':
    main()
