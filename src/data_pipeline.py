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
    html_str = response.text
    bs_obj = BeautifulSoup(html_str, 'html.parser')
    scsv = bs_obj.find('pre').getText()

    data = io.StringIO(scsv)
    df = pd.read_csv(data, sep=';')

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
    # Retrieve information on stats
    # stat_url = 'http://api.fantasy.nfl.com/v1/game/stats?format=json'
    # response = requests.get(stat_url)
    # stats = response.json()['stats']

    # # Create dictionary where the id is the key and the abbreviation of the stat
    # # is the value
    # stat_names = []
    # for stat in stats:
    #     stat_names.append(stat['abbr'])

    # Retrive stats for the given week and season in JSON format
    url = 'http://api.fantasy.nfl.com/v1/players/stats?'
    payload = {'week': week,
               'season': year,
               'format': 'json',
               'statType': 'weekStats'
              }
    response = requests.get(url, payload)

    # Convert to a pandas DataFrame
    df = pd.DataFrame(response.json()['players'])

    # 
    stats_df = df['stats'].apply(pd.Series)
    stats_df.fillna(0, inplace=True)
    stats_df.columns = stats_df.columns.map(int)

    for i in range(1,94):
        if i not in stats_df.columns:
            stats_df[i] = np.zeros(stats_df.shape[0])

    stats_df = stats_df[[i for i in range(1,94)]]
    stats_df.columns = stat_names
    df = pd.concat([df.drop(columns='stats'), stats_df], axis=1)

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

stat_names = ['gp',
              'att',
              'comp',
              'inc',
              'yds',
              'td',
              'int',
              'sacked',
              '300-399',
              '400+',
              '40+_td',
              '50+_td',
              'att',
              'yds',
              'td',
              '40+_td',
              '50+_td',
              '100-199',
              '200+',
              'rect',
              'yds',
              'td',
              '40+_td',
              '50+_td',
              '100-199',
              '200+',
              'yds',
              'td',
              'fum_td',
              'lost',
              'fum',
              '2pt',
              'made',
              'miss',
              '0-19',
              '20-29',
              '30-39',
              '40-49',
              '50+',
              '0-19',
              '20-29',
              '30-39',
              '40-49',
              '50+',
              'sack',
              'int',
              'fum_rec',
              'fum_f',
              'saf',
              'td',
              'block',
              'yds',
              'td',
              'pts_allow',
              'pts_allow',
              'pts_allow',
              'pts_allow',
              'pts_allow',
              'pts_allow',
              'pts_allow',
              'pts_allowed',
              'yds_allow',
              '0-99_yds',
              '100-199_yds',
              '200-299_yds',
              '300-399_yds',
              '400-449_yds',
              '450-499_yds',
              '500+_yds',
              'tot',
              'ast',
              'sck',
              'int',
              'frc_fum',
              'fum_rec',
              'int_td',
              'fum_td',
              'blk_td',
              'blk',
              'saf',
              'pdef',
              'int_yds',
              'fum_yds',
              'tfl',
              'qb_hit',
              'sck_yds',
              '10+_tackles',
              '2+_sacks',
              '3+_passes_defended',
              '50+_yard_int_return_td',
              '50+_yard_fumble_return_td',
              'dp_2pt_ret',
              'dst_2pt_ret']