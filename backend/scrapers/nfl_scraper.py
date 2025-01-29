import datetime

import pandas as pd
import numpy as np
import bs4
import re
import requests
from helpers.date_time_handler import DateTimeHandler
from models.club import Club
from models.league import League


class NFLScraper:
    """
    Static methods which perform the scraping functionality.

    Attributes
    ----------
        __leagues      Acts as a cache for storing league url/name
        __clubs        Acts as a cache for storing club   ids/names

    Methods
    -------
        __scrap_leagues():
            Scraps data containing a list of leagues.
        scrap_leagues():
            Calls __get_leagues if __leagues is None, otherwise, it retrieves __leagues immediately.

        __get_cached_clubs():
            Retrieves the club's snapshot.
        cache_clubs():
            Collects a snapshot of the clubs for faster fetch in the future.
        __get_clubs(leagues, tolerate_too_many_requests=False):
            Calls http://site.api.espn.com/apis/site/v2/sports/soccer/{league}/teams iteratively to fetch all clubs ids.
        get_clubs(leagues, tolerate_too_many_requests=False):
            Calls __get_clubs if __clubs is None, otherwise, it retrieves __clubs immediately.

        __get_cached_players():
            Retrieves the player's snapshot.
        cache_players():
            Collects a snapshot of the players for faster fetch in the future.
        scrap_players(season_years=None, leagues=None, clubs=None, fast_fetch_clubs=False, fast_fetch=False)
            Scraps data containing information about club's players.
        __scrap_players(season_years=None, leagues=None, clubs=None, fast_fetch_clubs=False):
            Scraps data containing information about club's players.

        __get_cached_matches():
            Retrieves the match's snapshot.
        cache_matches():
            Collects a snapshot of the matches for faster fetch in the future.
        scrap_matches(start_date=None, end_date=None, fast_fetch=False):
            Scraps data containing information about the results of the matches.
        __scrap_matches(start_date=datetime.date.today() - datetime.timedelta(days=7), end_date=datetime.date.today()):
            Scraps data containing information about the results of the matches.
    """

    __leagues = None
    __clubs = None
    __news = None

    @staticmethod
    def __get_cached_clubs():
        """
        Retrieves the club's snapshot.
        """

        clubs = []
        df = pd.read_csv('cached_clubs_nfl.csv', index_col='club_id', skiprows=1)

        for index, row in df.iterrows():
            clubs.append(Club(index, row['club_name'], League(row['league_url'], row['league_name'])))

        return clubs

    @staticmethod
    def cache_clubs():
        """
        Collects a snapshot of the clubs for faster fetch in the future.
        """
        clubs = NFLScraper.get_clubs()

        data = {
            'club_id': [x.club_id for x in clubs],
            'club_name': [x.name for x in clubs],
            
            'club_slug': [x.name for x in clubs],
            
            'club_abbreviation': [x.abbreviation for x in clubs],
            'club_display_name': [x.display_name for x in clubs],
            
            'club_short_display_name': [x.short_display_name for x in clubs],
            
            'club_location': [x.location for x in clubs],
            
            'league': ['nfl' for x in clubs],
            'players_url': [x.players_url for x in clubs],
        }

        df = pd.DataFrame(data)

        df.set_index('club_id', inplace=True)

        # f = open('cached_clubs_nba.csv', "w+")
        # #f.write(f'# Timestamp: {datetime.datetime.utcnow()}\n')
        # f.close()

        # noinspection PyTypeChecker
        df.to_csv('cached_clubs_nfl.csv', mode='a')
    
    @staticmethod
    def __get_clubs(fast_fetch=False):
        """
        Calls http://site.api.espn.com/apis/site/v2/sports/soccer/{league}/teams iteratively to fetch all clubs ids.

        :param bool tolerate_too_many_requests: Specify to whether throw an exception if the status code is not 200
        :param bool fast_fetch: Retrieves clubs from a saved snapshot instantly
        :return: A list of clubs object
        """

     
        clubs = []
        
        # Partially prevents scraping detection
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}

        response = requests.get(f'http://site.api.espn.com/apis/site/v2/sports/football/nfl/teams',
                                headers=headers)

        for club in response.json()['sports'][0]['leagues'][0]['teams']:
            team = club['team']
            link = club['team']['links']
            if len(link)!=0:
                href = club['team']['links'][1]['href']
            else:
                href = None
            clubs.append(Club(team['id'], team['name'], team['slug'], team['abbreviation'], team['displayName'], 
                               team['shortDisplayName'], team['location'], 'nfl',  href))

        return clubs
    
    @staticmethod
    def get_clubs(fast_fetch=False):
        """
        Calls __get_clubs if __clubs is None, otherwise, it retrieves __clubs immediately.

        :param bool fast_fetch: Retrieves clubs from a saved snapshot instantly
        :return: A list of clubs object
        """

        if NFLScraper.__clubs is None:
            print('Fetching clubs, this is a one time process...')
            NFLScraper.__clubs = NFLScraper.__get_clubs(fast_fetch=fast_fetch)
            print('Received clubs\n')

        return NFLScraper.__clubs.copy()
    
    
    @staticmethod
    def __get_cached_players():
        """
        Retrieves the player's snapshot.
        """

        players = pd.read_csv('cached_players_nfl.csv', skiprows=1)

        return players

    @staticmethod
    def cache_players():
        """
        Collects a snapshot of the players for faster fetch in the future.
        """
        players = NFLScraper.scrap_players(fast_fetch_clubs=False)

        # f = open('cached_clubs.csv', "w+")
        # f.write(f'# Timestamp: {datetime.datetime.utcnow()}\n')
        # f.close()

        # noinspection PyTypeChecker
        players.to_csv('cached_players_nfl.csv', mode='a')

    @staticmethod
    def scrap_players(season_years=None, leagues=None, clubs=None, fast_fetch_clubs=False, fast_fetch=False):
        """
        Scraps data containing information about club's players.

        :param list[int] season_years: Collect the data from the provided year(s)
        :param list[str] leagues: Specify the desired league(s)
        :param list[str] clubs: Specify the desired club(s)
        :param bool fast_fetch_clubs: Retrieves clubs from a saved snapshot instantly
        :param bool fast_fetch: Retrieves players from a saved snapshot instantly
        :return: A dataframe containing club players
        """

        if fast_fetch:
            df = NFLScraper.__get_cached_players()
            if clubs is not None:
                df = df[df.CLUB.isin(clubs)]
            return df

        else:
            return NFLScraper.__scrap_players(clubs, fast_fetch_clubs)

    @staticmethod
    def __scrap_players(clubs=None, fast_fetch_clubs=False):
        """
        Scraps data containing information about club's players.

        :param list[int] season_years: Collect the data from the provided year(s)
        :param list[str] leagues: Specify the desired league(s)
        :param list[str] clubs: Specify the desired club(s)
        :param bool fast_fetch_clubs: Retrieves clubs from a saved snapshot instantly
        :return: A dataframe containing club players
        """


        if fast_fetch_clubs:
            scraped_clubs = NFLScraper.__get_cached_clubs()
        else:
            scraped_clubs = NFLScraper.get_clubs()
            
        if clubs is not None and not all(isinstance(x, str) for x in clubs):
            raise ValueError('clubs must be a list of string')


        data = []
        columns = [	'NAME','POS',	'AGE',	'HT',	'WT',	'COLLEGE', 	'SALARY']
        for club in scraped_clubs:
            url = club.players_url 
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
            res = requests.get(url, headers=headers)
            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            tables = soup.find_all('table', attrs={'class': 'Table'})

            columns = [	'NAME','POS',	'AGE',	'HT',	'WT',	'EXP',	'COLLEGE', 'POSITION']
            data = []
            for x in np.arange(0, 5):
                
                rows = tables[x].find_all('tr')
                
                for row in rows:
                    cols = row.find_all('td')
                    
                    cols = [ele.text.strip() for ele in cols]  # Strips elements
                    if len(cols) !=0:
                        match x:
                            case 0:
                                cols.append('offence')
                            case 1:
                                cols.append('defence')
                            case 2:
                                cols.append('special')
                            case 3:    
                                cols.append('injured')
                            case 4:    
                                cols.append('practice')
                        data.append(cols[1:])

        df = pd.DataFrame(data)
        df.columns=columns
        return df
    
    
    @staticmethod
    def __get_cached_matches():
        """
        Retrieves the match's snapshot.
        """

        matches = pd.read_csv('cached_matches_nfl.csv', skiprows=1, dtype={'date': object,
                                                                       'club1': str,
                                                                       'SCORE': str,
                                                                       'club2': str,
                                                                       'DURATION': str,
                                                                       'LOCATION': str,
                                                                       'ATTENDANCE': str,
                                                                       'TIME': str,
                                                                       'TV': np.float})

        matches['ATTENDANCE'] = pd.to_numeric(matches['ATTENDANCE'].str.replace(',', ''), downcast='integer')
        matches['date'] = pd.to_datetime(matches['date']).dt.date

        return matches

    @staticmethod
    def cache_matches():
        """
        Collects a snapshot of the matches for faster fetch in the future.
        """

        matches = NFLScraper.scrap_matches(start_date=datetime.date(2002, 10, 1),
                                              end_date=datetime.date(2022, 5, 29))

        # f = open('cached_matches.csv', "w+")
        # f.write(f'# Timestamp: {datetime.datetime.utcnow()}\n')
        # f.close()

        # noinspection PyTypeChecker
        matches.to_csv('cached_matches_nfl.csv', index=False, mode='a')
    
    @staticmethod
    def scrap_matches(start_date=None, end_date=None, fast_fetch=False):
        """
        Scraps data containing information about the results of the matches.

        :param datetime.date start_date: Specify the start date of the search
        :param datetime.date end_date: Specify the end date of the search
        :param bool fast_fetch: Retrieves matches from a saved snapshot instantly
        :return: An array of two dataframe containing match results (0: Elapsed, 1: Fixtures)
        """

        if fast_fetch:
            df = NFLScraper.__get_cached_matches()
            if start_date is not None:
                df = df[df.date >= start_date]
            if end_date is not None:
                df = df[df.date <= end_date]
            return df

        else:
            return NFLScraper.__scrap_matches(start_date, end_date)

    @staticmethod
    def __scrap_matches(start_date=datetime.date.today() - datetime.timedelta(days=7),
                        end_date=datetime.date.today(),
                        request_tries=8):
        """
        Scraps data containing information about the results of the matches.

        :param datetime.date start_date: Specify the start date of the search
        :param datetime.date end_date: Specify the end date of the search
        :param int request_tries: Determine to number of tries for each webpage request whenever it fails
        :return: An array of two dataframe containing match results (0: Elapsed, 1: Fixtures)
        """
        
        start_date=datetime.date.today() - datetime.timedelta(days=37)
        end_date=datetime.date.today()
        days_between = DateTimeHandler.get_dates_between(start_date, end_date)
        columns = [	'TEAM1','TEAM2', 'RESULT', 'PASSING_LEADER', 'RUSHING_LEADER', 'RECEIVING_LEADER', 'DATE']
        data = []
        for singleDay in days_between:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
            res = requests.get(f'https://www.espn.in/nfl/schedule/_/date/{singleDay}', headers=headers)

            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            tables = soup.find_all('table', attrs={'class': 'Table'})
            for x in np.arange(0, len(tables)):
                
                rows = tables[x].find_all('tr')
                
                # Find the previous sibling with the class "table_name"
                previous = tables[x].find_previous(class_="Table__Title").text.strip()
                # if previous:
                #     print(f"Found header for table: {previous.text.strip()}")
                
                for row in rows:
                    cols = row.find_all('td')
                    
                    cols = [ele.text.strip() for ele in cols]  # Strips elements
                    
                    if len(cols) !=0:
                        cols=cols[:-1]
                        cols.append(previous)
                        data.append(cols)

        df = pd.DataFrame(data)
        df.columns=columns
        return df
    
    @staticmethod
    def __get_formatted_news():
        # Partially prevents scraping detection
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
        response = requests.get(f'http://site.api.espn.com/apis/site/v2/sports/football/nfl/news',
                                headers=headers)

        articles = response.json()['articles']
        links = []
        formated_articles = []
        for k, article in enumerate(articles):
            formated_article = {}
            formated_article['type'] =article['type']
            formated_article['headline'] =article['headline']
            formated_article['description'] =article['description']
            formated_article['lastModified'] =article['lastModified']
            formated_article['published'] =article['published']
            formated_article['dataSourceIdentifier'] =article['dataSourceIdentifier']
            formated_article['links'] = article['links']['web']['href']
            
            c = []
            for r in article['categories']:
                if r['type']!= 'guid':
                    d = {}
                    d['type'] = r['type']
                    d['desc'] = r['description']   
                    c.append(d)
            
            formated_article['categories'] = c
        
            try:
                formated_article['images'] = article['images']
            except:
                formated_article['images'] = []
            
            formated_articles.append(formated_article)
          
        return formated_articles
    
    @staticmethod
    def get_formatted_news(fast_fetch=False):
        if NFLScraper.__news is None:
            print('Fetching news, this is a one time process...')
            NFLScraper.__news = NFLScraper.__get_formatted_news()
            print('Received news\n')
        return NFLScraper.__news
    
    
    @staticmethod
    def get_news_images(fast_fetch=False):
        all_imgs = []
        for artic in NFLScraper.__news:
            img = {}
            categ = {}
            id = artic['dataSourceIdentifier']
            
            for im in artic['images']:
                img = {}
                img['name'] = im['name']
                
                if 'credit' in im.keys():
                    img['credit'] = im['credit']
                else:
                    img['credit'] = ''
                    
                if 'caption' in im.keys():
                    img['caption'] = im['caption']
                else:
                    img['caption'] = ''
                    
                if 'height' in im.keys():      
                    img['height'] = im['height']
                else:
                    img['height'] = ''
                    
                if 'width' in im.keys():     
                    img['width'] = im['width']
                else:
                    img['width'] = ''
                    
                img['url'] = im['url']
                img['article_id'] = id
                all_imgs.append(img)
        df = pd.DataFrame(all_imgs)
        return df
        
        
    @staticmethod
    def get_news_categories(fast_fetch=False):
        all_categs = []
        for artic in NFLScraper.__news:
            for cat in artic['categories']:
                categ = {}
                categ['type'] = cat['type']
                categ['description'] = cat['desc']
                categ['article_id'] = id
                all_categs.append(categ)
        df = pd.DataFrame(all_categs)
        return df