import requests
import pandas as pd
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from io import StringIO
import time


HLTV_LINK = 'https://www.hltv.org'


def get_response_text(link: str, params=None) -> str:
    """Returns the html markup of the page"""
    while True:
        user_agent = UserAgent().random
        response = requests.get(link, params=params, headers={'user-agent': user_agent})
        if response.status_code != 200:
            time.sleep(1)
        else:
            break
    return response.text


def get_majors():
    """Parses all past majors from the HLTV.org and saves data to CSV file"""
    hltv_archive_link = 'https://www.hltv.org/events/archive'
    response_text = get_response_text(hltv_archive_link, params={'eventType': 'MAJOR'})
    soup = BeautifulSoup(response_text, 'lxml')
    events = soup.find_all(class_='small-event')
    majors_df = pd.DataFrame()
    for event in events:
        prize: str = event.find(class_='prizePoolEllipsis').text
        if prize.startswith('$'):
            major_link = HLTV_LINK + event['href']
            major_id = major_link.split('/')[4]
            majors_df.loc[major_id, 'Event'] = event.find(class_='text-ellipsis').text
            majors_df.loc[major_id, 'Link'] = major_link
            majors_df.loc[major_id, 'Location'] = event.find(class_='col-desc').text.rstrip(' | ')
            majors_df.loc[major_id, 'Date'] = event.find_all(class_='col-desc')[1].text
            majors_df.loc[major_id, 'Prize'] = prize
    majors_df.to_csv('data/majors.csv', index_label='ID')


def get_majors_stats(obj: str):
    """Parses player or team stats for majors that are presented in majors.csv"""
    available_objs = ['player', 'team']
    if obj in available_objs:
        hltv_stats_link = f'https://hltv.org/stats/{obj}s'
        majors_df = pd.read_csv('data/majors.csv', index_col=0)
        major_ids = majors_df.index.to_list()
        dfs_list = []
        for major_id in major_ids:
            response_text = get_response_text(hltv_stats_link, params={'event': major_id})
            stats_df = pd.read_html(StringIO(response_text))[0]
            stats_df.insert(loc=0, column='Event ID', value=major_id)
            stats_df.rename(columns={'K-D Diff': 'K-D Diff'}, inplace=True)
            dfs_list.append(stats_df)
        pd.concat(dfs_list).to_csv(f'data/majors_{obj}_stats.csv', index=False)
