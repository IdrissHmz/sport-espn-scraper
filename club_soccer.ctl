LOAD DATA
INFILE 'soccer_clubs.csv'
INTO TABLE soccer_clubs
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
(
    club_id,
    club_name,
    league_url,
    league_name
)