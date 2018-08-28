import requests
from bs4 import BeautifulSoup
import io
import pandas as pd
import numpy as np
import psycopg2
from sqlalchemy import create_engine, inspect

def rotoguru_scrape(week=1, year=2017):
    '''
    This function scrapes the DraftKings data from rotoguru.

    PARAMETERS
    ----------
    week: {int} the week of the NFL season
    
    year: {int} the NFL season year

    RETURNS
    -------
    df: {pandas.DataFrame} a DataFrame containing the data
    '''
    url = 'http://rotoguru1.com/cgi-bin/fyday.pl?'
    payload = {'week': week,
               'year': year,
               'game': 'dk',
               'scsv': 1
              }
    response = requests.get(url, payload)

    if response.status_code != 200:
        return False

    html_str = response.text
    bs_obj = BeautifulSoup(html_str, 'html.parser')
    scsv = bs_obj.find('pre').getText()

    # Read string to DataFrame
    data = io.StringIO(scsv)
    df = pd.read_csv(data, sep=';')
    # Set columns to lowercase and remove non-alphanumeric characters
    df.columns = df.columns.map(lambda x: ''.join(c for c in x if c.isalnum()).lower())

    # Reformat name column
    new_names=[]
    for i, name in enumerate(df['name']):
        if ',' in name:
            names = name.split(', ')
            names.reverse()
            name = ' '.join(names)
        new_names.append(name)

    df['name'] = new_names

    # Capitalize positions and teams
    df['pos'] = df['pos'].map(lambda x: x.upper())
    df['team'] = df['team'].map(lambda x: x.upper())

    return df

def stat_scrape(week=1, year=2017):
    '''
    This function scrapes the passer stats from NFL's fantasy api.

    PARAMETERS
    ----------
    week: {int} the week of the NFL season
    
    year: {int} the NFL season year

    RETURNS
    -------
    scsv: {str} a string containing the semi-colon separated data
    '''
    # Retrive stats for the given week and season in JSON format
    url = 'http://api.fantasy.nfl.com/v1/players/stats?'
    payload = {'week': week,
                'season': year,
                'format': 'json',
                'statType': 'weekStats'
                }
    response = requests.get(url, payload)

    if response.status_code != 200:
        return False

    # Convert to a pandas DataFrame
    df = pd.DataFrame(response.json()['players'])

    df.columns = df.columns.map(lambda x: ''.join(c for c in x \
                            if c.isalnum()).lower())

    # Parse out stats
    stats_df = df['stats'].apply(pd.Series)
    stats_df.fillna(0, inplace=True)
    stats_df.columns = stats_df.columns.map(int)

    for i in range(1,94):
        if i not in stats_df.columns:
            stats_df[i] = np.zeros(stats_df.shape[0])

    stats_df = stats_df[[i for i in range(1,94)]]
    stats_df.columns = stat_names
    df = pd.concat([df.drop(columns='stats'), stats_df], axis=1)
    df['week'] = np.zeros(df.shape[0], dtype=int) + week
    df['year'] = np.zeros(df.shape[0], dtype=int) + year

    return df

def to_database(df, table_name):
    '''
    This function takes the web-scraped data and inserts it to a Postgres
    database

    PARAMETERS
    ----------
    scsv: {str} a string containing the semi-colon separated data
    table_name: {str} table name

    RETURNS
    -------
    None
    '''
    engine = create_engine("postgresql+psycopg2://football:isback@localhost/nfl")
    df.to_sql(table_name, engine, if_exists='append', index=False)

    return

# Retrieve information on stats
stat_url = 'http://api.fantasy.nfl.com/v1/game/stats?format=json'
response = requests.get(stat_url)
stats = response.json()['stats']

# Create list where the id is the key and the abbreviation of the stat
# is the value
stat_names = []
for stat in stats:
    stat_names.append(stat['name'])

# Clean stat_names
stat_names = [name.replace(' ', '_') for name in stat_names]
stat_names = [name.replace('+', '_plus') for name in stat_names]
stat_names = [name.replace('-', '_to_') for name in stat_names]
stat_names = [name.replace('(','') for name in stat_names]
stat_names = [name.replace(')','') for name in stat_names]
stat_names = [name.lower() for name in stat_names]

if __name__ == '__main__':
    for i in range(1,18):
        dk_df = rotoguru_scrape(week=i)

        if type(dk_df) != pd.DataFrame:
            print('Failed to retrieve DraftKings data for Week {}'.format(i))
        else:
            print('Successfully retrieved DraftKings data for Week {}'.format(i))
            to_database(dk_df, table_name='draftkings')

        stat_df = stat_scrape(week=i)

        if type(stat_df) != pd.DataFrame:
            print('Failed to retrieve fantasy stats for Week {}'.format(i))
        else:
            print('Successfully retrieved fantasy stats for Week {}'.format(i))
            to_database(stat_df, table_name='stats')

        