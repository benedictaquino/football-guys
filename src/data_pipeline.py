import requests
from bs4 import BeautifulSoup
import io
import pandas as pd
import numpy as np
import psycopg2
from sqlalchemy import create_engine

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
    for name in df['name']:
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
    stats_df = df['stats'].apply(pd.Series, dtype=float)
    stats_df.fillna(0, inplace=True)
    stats_df.columns = stats_df.columns.map(int)

    for i in range(1,94):
        if i not in stats_df.columns:
            stats_df[i] = np.zeros(stats_df.shape[0])

    stats_df = stats_df[[i for i in range(1,94)]]
    stats_df.columns = stat_names

    # Kickoff and punt return yards and touchdowns are duplicates
    stats_df.drop(columns='duplicate')

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

# Postgres does not like columns that begin with integers
stat_names[31] = 'two_point_conversions'

# Kickoff and punt return yards/touchdowns are duplicates
stat_names[51] = 'duplicate'
stat_names[52] = 'duplicate'

# Clean stat_names
stat_names = [name.replace(' ', '_') for name in stat_names]
stat_names = [name.replace('+', 'plus') for name in stat_names]
stat_names = [name.replace('-', '_') for name in stat_names]
stat_names = list(map((lambda x: ''.join(c for c in x if (c.isalnum() or c == '_')).lower()), stat_names))



def query_avg(pos_string=''):
    engine = create_engine("postgresql+psycopg2://football:isback@localhost/nfl")
    '''
    This function queries the database and returns a pandas DataFrame containing
    the id, name, position, and weekly average fantasy points of the players by
    position

    PARAMETERS
    ----------
    pos_string: {str} to filter out certain positions, default returns all

    RETURNS
    -------
    {pandas.DataFrame} a DataFrame containing the relevant data

    '''
    q = '''
    SELECT id,
        name,
        position AS pos,
        AVG(weekpts) AS avg_points,
        AVG(passing_attempts) AS avg_passing_attempts,
        AVG(passing_completions) AS avg_passing_completions,
        AVG(incomplete_passes) AS avg_incomplete_passes,
        AVG(passing_yards) AS avg_passing_yards,
        AVG(passing_touchdowns) AS avg_passing_touchdowns,
        AVG(interceptions_thrown) AS avg_interceptions_thrown,
        AVG(every_time_sacked) AS avg_every_time_sacked,
        AVG(rushing_attempts) AS avg_rushing_attempts,
        AVG(rushing_yards) AS avg_rushing_yards,
        AVG(rushing_touchdowns) AS avg_rushing_touchdowns,
        AVG(receptions) AS avg_receptions,
        AVG(receiving_yards) AS avg_receiving_yards,
        AVG(receiving_touchdowns) AS avg_receiving_touchdowns,
        AVG(kickoff_and_punt_return_yards) AS avg_kickoff_and_punt_return_yards,
        AVG(kickoff_and_punt_return_touchdowns) AS avg_kickoff_and_punt_return_touchdowns,
        AVG(fumble_recovered_for_td) AS avg_fumble_recovered_for_td,
        AVG(fumbles_lost) AS avg_fumbles_lost,
        AVG(fumble) AS avg_fumble,
        AVG(two_point_conversions) AS avg_2_point_conversions,
        AVG(pat_made) AS avg_pat_made,
        AVG(pat_missed) AS avg_pat_missed,
        AVG(fg_made_0_19) AS avg_fg_made_0_19,
        AVG(fg_made_20_29) AS avg_fg_made_20_29,
        AVG(fg_made_30_39) AS avg_fg_made_30_39,
        AVG(fg_made_40_49) AS avg_fg_made_40_49,
        AVG(fg_made_50plus) AS avg_fg_made_50plus,
        AVG(fg_missed_0_19) AS avg_fg_missed_0_19,
        AVG(fg_missed_20_29) AS avg_fg_missed_20_29,
        AVG(fg_missed_30_39) AS avg_fg_missed_30_39,
        AVG(fg_missed_40_49) AS avg_fg_missed_40_49,
        AVG(fg_missed_50plus) AS avg_fg_missed_50plus,
        AVG(sacks) AS avg_sacks,
        AVG(interceptions) AS avg_interceptions,
        AVG(fumbles_recovered) AS avg_fumbles_recovered,
        AVG(fumbles_forced) AS avg_fumbles_forced,
        AVG(safeties) AS avg_safeties,
        AVG(touchdowns) AS avg_touchdowns,
        AVG(blocked_kicks) AS avg_blocked_kicks,
        AVG(points_allowed) AS avg_points_allowed,
        AVG(yards_allowed) AS avg_yards_allowed,
        AVG(tackle) AS avg_tackle,
        AVG(assisted_tackles) AS avg_assisted_tackles,
        AVG(sack) AS avg_sack,
        AVG(defense_interception) AS avg_defense_interception,
        AVG(forced_fumble) AS avg_forced_fumble,
        AVG(fumbles_recovery) AS avg_fumbles_recovery,
        AVG(touchdown_interception_return) AS avg_touchdown_interception_return,
        AVG(touchdown_fumble_return) AS avg_touchdown_fumble_return,
        AVG(touchdown_blocked_kick) AS avg_touchdown_blocked_kick,
        AVG(blocked_kick_punt_fg_pat) AS avg_blocked_kick_punt_fg_pat,
        AVG(safety) AS avg_safety,
        AVG(pass_defended) AS avg_pass_defended,
        AVG(interception_return_yards) AS avg_interception_return_yards,
        AVG(fumble_return_yards) AS avg_fumble_return_yards,
        AVG(qb_hit) AS avg_qb_hit,
        AVG(sack_yards) AS avg_sack_yards,
        AVG(def_2_point_return) AS avg_def_2_point_return,
        AVG(team_def_2_point_return) AS avg_team_def_2_point_return
    FROM fantasy
    GROUP BY id, name, pos
    HAVING position = '{}'
    ORDER BY avg_points DESC;
    '''.format(pos_string)

    return pd.read_sql(q, engine)

def query_week(week=1, pos='QB'):
    engine = create_engine("postgresql+psycopg2://football:isback@localhost/nfl")
    '''
    This function queries the database and returns a pandas DataFrame containing
    the id, name, position, and stats for a given week

    PARAMETERS
    ----------
    week: {int}

    RETURNS
    -------
    {pandas.DataFrame} a DataFrame containing the relevant data

    '''
    q = '''
    SELECT id,
        name,
        position AS pos,
        weekpts,
        passing_attempts,
        passing_completions,
        incomplete_passes,
        passing_yards,
        passing_touchdowns,
        interceptions_thrown,
        every_time_sacked,
        rushing_attempts,
        rushing_yards,
        rushing_touchdowns,
        receptions,
        receiving_yards,
        receiving_touchdowns,
        kickoff_and_punt_return_yards,
        kickoff_and_punt_return_touchdowns,
        fumble_recovered_for_td,
        fumbles_lost,
        fumble,
        two_point_conversions,
        pat_made,
        pat_missed,
        fg_made_0_19,
        fg_made_20_29,
        fg_made_30_39,
        fg_made_40_49,
        fg_made_50plus,
        fg_missed_0_19,
        fg_missed_20_29,
        fg_missed_30_39,
        fg_missed_40_49,
        fg_missed_50plus,
        sacks,
        interceptions,
        fumbles_recovered,
        fumbles_forced,
        safeties,
        touchdowns,
        blocked_kicks,
        points_allowed,
        yards_allowed,
        tackle,
        assisted_tackles,
        sack,
        defense_interception,
        forced_fumble,
        fumbles_recovery,
        touchdown_interception_return,
        touchdown_fumble_return,
        touchdown_blocked_kick,
        blocked_kick_punt_fg_pat,
        safety,
        pass_defended,
        interception_return_yards,
        fumble_return_yards,
        qb_hit,
        sack_yards,
        def_2_point_return,
        team_def_2_point_return
    FROM fantasy
    WHERE week = {}
    AND position = '{}'
    ORDER BY weekpts DESC;
    '''.format(week, pos)

    return pd.read_sql(q, engine)

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
            to_database(stat_df, table_name='fantasy')

        