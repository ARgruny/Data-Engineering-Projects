# Data Warehose & ETL process for Sparkify

## Summary
- Project scope
- Steps for setting up the database
- ETL process
- Checking final setup
- Database tables and structure
- Example Queries

## Project scope
A music streaming startup, Sparkify, has grown their user base and song database and want to move their processes and data onto the cloud. Their data resides in S3, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

The target for Sparkify is to set up a AWS cloud hosted datawarehouse using the Amazon Redshift service. 

## Steps for setting up the database

#### 1. Configuration of resources
Use the two .cfg config files and insert the configuration of the DWH. The 'cluster.cfg' is used to start and set up the AWS resources. The 'dwh.cfg' file is used for the ETL process. The start_cluster script will write back into the 'dwh.cfg' file so make sure that no field is deleted, even the empty HOST and ARN field.

#### 2. Setting up the DWH resources
2 Scripts are provided to control the DWH infrstructure. Use the following commands to start up the Redshift cluster

##### **start_cluster.py** - this script uses the boto3 liabry to programatically sart AWS resources. It can run for a few minutes as it waits for aws to set up the resource.
- use `python start_cluster.py` in your cmd console

##### **delete_cluster.py** - this script will delete all resources set up by the start_cluster script.
- use `python delete_cluster.py` in your cmd console

## ETL process
The ETL process is managed by 2 scripts. 
- **create_tables.py** - this script will drop the tables if they exist and create the again to provide a clean set up. 
- **etl.py** - this script will first load the data from AWS S3 into the staging tables and then transform the data before it is inserted into the database tables

both scripts can be executed using the command line:

`python create_tables.py`

`python etl.py`

## Checking the setup

After the ETL process is finished. All tables can be checked and used for anaytical work.
I.e. a simple check is to query the count of rows for a table by calling:
`SELECT COUNT(*) as total FROM table`

## Database tables and structure
To run the analytical queries a simple star schema was built. 

#### Table Specifications

##### Song Play Table

- **title**: fact_songplay
- **type**: Fact table

| Column | Datatype | Notes |
| ------ | -------- | ----- |
| `songplay_id` | `INTEGER IDENTITY(0,1) SORTKEY` | primary key and identificator for the table |
| `start_time` | `TIMESTAMP` | timestamp for song |
| `user_id` | `INTEGER NOT NULL REFERENCES dim_user (user_id)` | the user_id associated with the play event of the song. This can not be null |
| `level` | `VARCHAR` | membership level of user |
| `song_id` | `VARCHAR REFERENCES dim_songs (song_id)` | identificaor for the played song. This can be null |
| `artist_id` | `VARCHAR REFERENCES dim_artists (artist_id)` | identificator for the artist of the song. This can not be null |
| `session_id` | `INTEGER` | identificator for the session. |
| `location` | `VARCHAR` | the location from where the event was executed |
| `user_agent` | `VARCHAR` | agent used for the Sparkify app i.e Chrome, Firefox |

##### User Table

- **title**: dim_user
- **type**: Dimension table

| Column | Datatype | Notes |
| ------ | -------- | ----- |
| `user_id` | `INTEGER PRIMARY KEY` | the user_id associated with the play event of the song. |
| `first_name` | `VARCHAR NOT NULL` | first name of the user |
| `last_name` | `VARCHAR NOT NULL` | last name of the user |
| `gender` | `VARCHAR` | gender of the user |
| `level` | `VARCHAR NOT NULL` | membership level of user |

##### Song Table

- **title**: dim_song
- **type**: Dimension table

| Column | Datatype | Notes |
| ------ | -------- | ----- |
| `song_id` | `VARCHAR PRIMARY KEY` | identificaor for the played song |
| `title` | `VARCHAR NOT NULL SORTKEY` | title of the played song. this should not be null as it is the main information about a song |
| `artist_id` | `VARCHAR NOT NULL DISTKEY REFERENCES dim_artist (artist_id)` | identificator for the artist of the song. we choss this as a distkey as it provides a good distribution (no skewed data) |
| `year` | `INTEGER` | release year of the played song |
| `duration` | `FLOAT` | duration of the played song |

##### Artist Table

- **title**: dim_artist
- **type**: Dimension table

| Column | Datatype | Notes |
| ------ | -------- | ----- |
| `artist_id` | `VARCHAR PRIMARY KEY` | identificator for the artist of the song |
| `name` | `VARCHAR NOT NULL` | name of the artist |
| `location` | `VARCHAR` | the location from where the event was executed |
| `latitude` | `FLOAT` | The latitude coordinate of the location |
| `longitude` | `FLOAT` | The longitude coordinate of the location |

##### Time Table

- **title**: dim_time
- **type**: Dimension table

| Column | Datatype | Notes |
| ------ | -------- | ----- |
| `start_time` | `TIMESTAMP NOT NULL PRIMARY KEY` | timestamp for song |
| `hour` | `INTEGER NOT NULL` | The hour from the timestamp  |
| `day` | `INTEGER NOT NULL` | The day of the month from the timestamp |
| `week` | `INTEGER NOT NULL` | The week of the year from the timestamp |
| `month` | `INTEGER NOT NULL` | The month of the year from the timestamp |
| `year` | `INTEGER NOT NULL` | The year from the timestamp |
| `weekday` | `INTEGER NOT NULL` | The week day from the timestamp |

#### Staging Tables

The process needs two staging tables to preload the data befor it is transformed.

##### Events Table

- **title**: staging_events
- **type**: Staging table

| Column | Datatype | Notes |
| ------ | -------- | ----- |
| `artist` | `VARCHAR` | artist name |
| `auth` | `VARCHAR` | authentication status |
| `firstName` | `VARCHAR` | first name of the user |
| `gender` | `VARCHAR` | gender of the user |
| `itemInSession` | `INTEGER` | number of the item during a  session |
| `lastName` | `VARCHAR` | last name of the user |
| `length` | `FLOAT` | duration of the song |
| `level` | `VARCHAR` | membership level of user |
| `location` | `VARCHAR` | location of the user |
| `method` | `VARCHAR` | method of the http request |
| `page` | `VARCHAR` | source page that the event occurred |
| `registration` | `BIGINT` | time that the user registered |
| `sessionId` | `INTEGER` | session id |
| `song` | `VARCHAR` | song title |
| `status` | `INTEGER` | status |
| `ts` | `BIGINT` | timestamp for this event |
| `userAgent` | `VARCHAR` | agent used for the Sparkify app i.e Chrome, Firefox |
| `userId` | `INTEGER` | user id |

##### Songs Table

- **title**: staging_songs
- **type**: Staging table

| Column | Datatype | Notes |
| ------ | -------- | ----- |
| `num_songs` | `INTEGER` | number of songs of this artist |
| `artist_id` | `VARCHAR` | artist id |
| `artist_latitude` | `FLOAT` | latitude coordinate |
| `artist_longitude` | `FLOAT` | longitude coordinate |
| `artist_location` | `VARCHAR` | artist location |
| `artist_name` | `VARCHAR` | artist name |
| `song_id` | `VARCHAR` | song id |
| `title` | `VARCHAR` | title |
| `duration` | `Float` | duration of the song |
| `year` | `INTEGER` | year of the song |

## Example Query

Count of songs play per year per title
`SELECT s.year, a.name, COUNT(a.name) as num_played FROM fact_songplay f
 JOIN dim_song s ON f.song_id = s.song_id
 JOIN dim_artist a ON f.artist_id = a.artist_id
 GROUP BY s.year, a.name`
 
 
    
