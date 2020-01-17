import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# LOAD VARIABLES

LOG_DATA = config.get("S3","LOG_DATA")
LOG_PATH = config.get("S3", "LOG_JSONPATH")
SONG_DATA = config.get("S3", "SONG_DATA")
IAM_ROLE = config.get("IAM_ROLE","ARN")

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS satging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS fact_songplay"
user_table_drop = "DROP TABLE IF EXISTS dim_user"
song_table_drop = "DROP TABLE IF EXISTS dim_song"
artist_table_drop = "DROP TABLE IF EXISTS dim_artist"
time_table_drop = "DROP TABLE IF EXISTS dim_time"

# CREATE TABLES

staging_events_table_create= ("""
CREATE TABLE IF NOT EXISTS staging_events
(
    artist         VARCHAR,
    auth           VARCHAR,
    firstName      VARCHAR,
    gender         VARCHAR,
    itemInSession  INTEGER,
    lastName       VARCHAR,
    length         FLOAT,
    level          VARCHAR,
    location       VARCHAR,
    method         VARCHAR,
    page           VARCHAR,
    registration   BIGINT,
    sessionId      INTEGER,
    song           VARCHAR,
    status         INTEGER,
    ts             BIGINT,
    userAgent      VARCHAR,
    userId         INTEGER
);
""")

staging_songs_table_create = ("""
CREATE TABLE IF NOT EXISTS staging_songs
(
    num_songs           INTEGER,
    artist_id           VARCHAR,
    artist_latitude     FLOAT,
    artist_longitude    FLOAT,
    artist_location     VARCHAR,
    artist_name         VARCHAR,
    song_id             VARCHAR,
    title               VARCHAR,
    duration            FLOAT,
    year                INTEGER
);
""")

songplay_table_create = ("""
CREATE TABLE IF NOT EXISTS fact_songplay
(
    songplay_id    INTEGER IDENTITY(0,1),
    start_time     TIMESTAMP NOT NULL,
    user_id        INTEGER NOT NULL REFERENCES dim_user (user_id),
    level          VARCHAR,
    song_id        VARCHAR REFERENCES dim_song (song_id),
    artist_id      VARCHAR REFERENCES dim_artist (artist_id),
    session_id     INTEGER NOT NULL,
    location       VARCHAR,
    user_agent     VARCHAR
) SORTKEY(songplay_id);
""")

user_table_create = ("""
CREATE TABLE IF NOT EXISTS dim_user
(
    user_id        INTEGER PRIMARY KEY,
    first_name     VARCHAR NOT NULL,
    last_name      VARCHAR NOT NULL,
    gender         VARCHAR,
    level          VARCHAR NOT NULL
);
""")

song_table_create = ("""
CREATE TABLE IF NOT EXISTS dim_song
(
    song_id        VARCHAR PRIMARY KEY,
    title          VARCHAR NOT NULL,
    artist_id      VARCHAR NOT NULL REFERENCES dim_artist (artist_id),
    year           INTEGER,
    duration       FLOAT
) DISTKEY(artist_id) SORTKEY(title);
""")

artist_table_create = ("""
CREATE TABLE IF NOT EXISTS dim_artist
(
    artist_id      VARCHAR PRIMARY KEY,
    name           VARCHAR NOT NULL,
    location       VARCHAR,
    latitude       FLOAT,
    longitude      FLOAT 
);
""")

time_table_create = ("""
CREATE TABLE IF NOT EXISTS dim_time
(
    start_time     TIMESTAMP PRIMARY KEY,
    hour           INTEGER NOT NULL,
    day            INTEGER NOT NULL,
    week           INTEGER NOT NULL,
    month          INTEGER NOT NULL,
    year           INTEGER NOT NULL,
    weekday        INTEGER NOT NULL
);
""")

# STAGING TABLES

staging_events_copy = ("""
    COPY staging_events FROM {}
    CREDENTIALS 'aws_iam_role={}'
    COMPUPDATE OFF REGION 'us-west-2'
    TIMEFORMAT as 'epochmillisecs'
    TRUNCATECOLUMNS BLANKSASNULL EMPTYASNULL
    FORMAT AS JSON {}
""").format(LOG_DATA, IAM_ROLE, LOG_PATH)

staging_songs_copy = ("""
    COPY staging_songs FROM {}
    CREDENTIALS 'aws_iam_role={}'
    COMPUPDATE OFF REGION 'us-west-2'
    FORMAT AS JSON 'auto'
    TRUNCATECOLUMNS BLANKSASNULL EMPTYASNULL
""").format(SONG_DATA, IAM_ROLE)

# FINAL TABLES

songplay_table_insert = ("""
    INSERT INTO fact_songplay (start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
    SELECT DISTINCT TIMESTAMP 'epoch' + ts/1000 * interval '1 second' as start_time,
                    e.userId as user_id,
                    e.level as level,
                    s.song_id as song_id,
                    s.artist_id as artisit_id,
                    e.sessionId as session_id,
                    e.location as location,
                    e.userAgent as user_agent
    FROM staging_events e
    JOIN staging_songs s ON e.song = s.title AND e.artist = s.artist_name;
                    
""")

user_table_insert = ("""
    INSERT INTO dim_user (user_id, first_name, last_name, gender, level)
    SELECT DISTINCT userId as user_id,
                    firstName as first_name,
                    lastName as last_name,
                    gender as gender,
                    level as level
    FROM staging_events
    WHERE userId IS NOT NULL;
""")

song_table_insert = ("""
    INSERT INTO dim_song (song_id, title, artist_id, year, duration)
    SELECT DISTINCT song_id as song_id,
                    title as title,
                    artist_id as artist_id,
                    year as year,
                    duration as duration
    FROM staging_songs
    WHERE song_id IS NOT NULL
                    
""")

artist_table_insert = ("""
    INSERT INTO dim_artist (artist_id, name, location, latitude, longitude)
    SELECT DISTINCT artist_id as artist_id,
                    artist_name as name,
                    artist_location as location,
                    artist_latitude as latitude,
                    artist_longitude as longitude
    FROM staging_songs
    WHERE artist_id IS NOT NULL;
""")

time_table_insert = ("""
    INSERT INTO dim_time (start_time, hour, day, week, month, year, weekday)
    SELECT DISTINCT ts as start_time,
                EXTRACT(hour FROM ts),
                EXTRACT(day FROM ts),
                EXTRACT(week FROM ts),
                EXTRACT(month FROM ts),
                EXTRACT(year FROM ts),
                EXTRACT(weekday FROM ts)
    FROM (SELECT DISTINCT TIMESTAMP 'epoch' + ts/1000 * interval '1 second' as ts FROM staging_events)
    WHERE start_Time IS NOT NULL;
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, artist_table_create, user_table_create, song_table_create, time_table_create, songplay_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
