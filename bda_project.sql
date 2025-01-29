-- Create table for soccer_clubs with updated columns
CREATE TABLE soccer_clubs (
    club_id NUMBER PRIMARY KEY,
    club_name VARCHAR2(255),
    league_url VARCHAR2(255),
    league_name VARCHAR2(255)
);

DROP TABLE soccer_players;
-- Create table for soccer_matches (including player statistics)
CREATE TABLE soccer_players (
    player_id NUMBER PRIMARY KEY,
    year NUMBER,
    league VARCHAR2(255),
    club VARCHAR2(255),
    player_name VARCHAR2(255),
    player_number NUMBER,
    position VARCHAR2(50),
    age NUMBER,
    height NUMBER,
    weight NUMBER,
    nationality VARCHAR2(50),
    appearances NUMBER,
    substitutions NUMBER,
    saves NUMBER,
    goals_against NUMBER,
    assists NUMBER,
    fouls_committed NUMBER,
    fouls_against NUMBER,
    yellow_cards NUMBER,
    red_cards NUMBER,
    goals NUMBER,
    shots NUMBER,
    starts NUMBER
);

DROP TABLE soccer_matches;
-- Create table for soccer_matches (match details)
CREATE TABLE soccer_matches (
    match_id NUMBER PRIMARY KEY,
    match_date DATE,
    club1 VARCHAR2(255),
    score VARCHAR2(50),
    club2 VARCHAR2(255),
    duration VARCHAR2(50),
    location VARCHAR2(255),
    attendance NUMBER,
    time VARCHAR2(50),
    tv_broadcast VARCHAR2(255)
);


SELECT * FROM SOCCER_CLUBS;

SELECT * FROM SOCCER_MATCHES;
DELETE FROM soccer_matches;

SELECT * FROM SOCCER_PLAYERS;










CREATE SEQUENCE match_id_seq
START WITH 1
INCREMENT BY 1;

CREATE OR REPLACE TRIGGER soccer_matches_trigger
BEFORE INSERT ON soccer_matches
FOR EACH ROW
BEGIN
  :NEW.match_id := match_id_seq.NEXTVAL;
END;
/



CREATE SEQUENCE player_id_seq
START WITH 1
INCREMENT BY 1;

CREATE OR REPLACE TRIGGER soccer_players_trigger
BEFORE INSERT ON soccer_players
FOR EACH ROW
BEGIN
  :NEW.player_id := player_id_seq.NEXTVAL;
END;
/