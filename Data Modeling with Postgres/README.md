## Project Context

A startup called Sparkify wants to analyze the data they've been collecting on songs and user activity on their new music streaming app. The analytics team is particularly interested in understanding what songs users are listening to. urrently, they don't have an easy way to query their data, which resides in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

Target for Sparkify is to create a database schema and ETL pipeline optimized for this analysis.

## Data

The data is provided through two sources.
- **Song dataset**: JSON files, nested in subdirectories. A data sample of such files is:

```
{"num_songs": 1, "artist_id": "ARJIE2Y1187B994AB7", "artist_latitude": null, "artist_longitude": null, "artist_location": "", "artist_name": "Line Renaud", "song_id": "SOUPIRU12A6D4FA1E1", "title": "Der Kleine Dompfaff", "duration": 152.92036, "year": 0}
```

- **Log dataset**: JSON files, nested in subdirectories. A data sample of such files is: 

```
{"artist":"Slipknot","auth":"Logged In","firstName":"Aiden","gender":"M","itemInSession":0,"lastName":"Ramirez","length":192.57424,"level":"paid","location":"New York-Newark-Jersey City, NY-NJ-PA","method":"PUT","page":"NextSong","registration":1540283578796.0,"sessionId":19,"song":"Opium Of The People (Album Version)","status":200,"ts":1541639510796,"userAgent":"\"Mozilla\/5.0 (Windows NT 6.1) AppleWebKit\/537.36 (KHTML, like Gecko) Chrome\/36.0.1985.143 Safari\/537.36\"","userId":"20"}
```

## Planned DB Schema

According to the context of the project the aim of the databse is predominantly analytical work. The Star Schema can be useful for this type of database.
Analytical queries are typically at higher aggregation levels. Through the partial sacrifice of the normalization the most complex sql queries can be avoided. 
The Star Schema saves a lot of JOIN clauses which speeds up the read operations of queries. 

The Star Schema consists of one fact table containing all the measures derived from the events (in this case user song plays). 
In the described project case the schema also consists of 4 dimensional tables, each with a primary key that is being referenced from the fact table.

further reasons on why the star schema  and a relational database is useful for the case in this project context:
- the database works with structured data, which can be analyzed beforehand. An optimal schema an relational model can be derived. 
- the data volume is small therefore no big data solution is needed.
- for this kind of analysis the SQL language is sufficient.
- the data can be modeled using the standard ERD methods.
- the use of JOINS is necessary

## Definition of Tables

### Fact Table

**songplays** - records in log data associated with song plays i.e. records with page NextSong

- songplay_id (INTEGER) PRIMARY KEY: ID of each user song play
- start_time (TIMESTAMP) NOT NULL: Timestamp if beginning, used as key for JOINS
- user_id (INTEGER) NOT NULL: ID of user, used as key for JOINS
- level (VARCHAR): Level/account type of user (free|paid)
- song_id (VARCHAR) NOT NULL: ID of song played, used as key for JOINS
- artist_id (VARCHAR) NOT NULL: ID of artist of the song, used as key for JOINS
- session_id (INTEGER): ID of the session
- location (VARCHAR): User location
- user_agent (VARCHAR): Agent used by user, i.e. Web browser

### Dimension Tables

**songs** - songs in music database

- song_id (VARCHAR) PRIMARY KEY: ID of song
- title (VARCHAR): Title of song
- artist_id (VARCHAR): ID of artist
- year (INTEGER): Year of song
- duration (FLOAT): duration in milliseconds

**users** - users in the app

- user_id (INTEGER) PRIMARY KEY: ID of user
- first_name (VARCHAR): First name of user
- last_name (VARCHAR): Last name of user
- gender (CHAR): Gender of user (M | F)
- level (VARCHAR): User account type (free | paid)

**artists** - artists in music database

- artist_id (VARCHAR) PRIMARY KEY: ID of artist
- name (VARCHAR) NOT NULL: Name of artist
- location (VARCHAR): Name of city
- lattitude (FLOAT): Lattitude coordinate
- longitude (FLOAT): Longitude coordinate

**time** - timestamps of records in songplays broken down into specific units

- start_time (TIMESTAMP) PRIMARY KEY: Timestamp of the beginning of play
- hour (INTEGER): Hour derived from start time
- day (INTEGER): Day derived from start time
- week (INTEGER): Week of year derived from start time
- month (INTEGER): Month derived from start time
- year (INTEGER): Year derived from start time
- weekday (INTEGER): Weekday as integer from 1 to 7 derived from start time

## Design of ETL Pipeline

#### Prerequisites:

The Database and the tables described above must be created before the start of the ETL pipeline. Run create_tables.py to do this. 

#### Steps of ETL Pipeline

1. The ETL pipeline start by importing all necessary python libaries. 
2. Python connects to the sparkify database and precesses all nested JSON files for the song data.
3. The script walks through all JSON files under '/data/song_data' each file is then send to the process_song_file function.
4. The process_song_file function uses the read_json() method of the pandas libary and select the interesting data by calling the corresponding column names.

    ```
    song_data = [song_id, title, artist_id, year, duration]
    ```
    
    ```
     artist_data = [artist_id, artist_name, artist_location, artist_longitude, artist_latitude]
    ```
5. After assigning the data to a new dataframe, the script inserts the data into the respective database and table.
6. After all files of the song data are processed the script moves on to the log data.
7. Step 2 is repeated but all found files are now send to the process_log_file function.
8. Again the data is read into a pandas dataframe and only the wanted data is assigned to a new smaller dataframe. Using a filter on the column page and the corresponding value 'NextSong'
9. The timestamp column is converted into a datetime format. All features formulated in the time table of the database are obtained through the pandas series.dt method. 
10. The datetime, timestamp data is load into the database.
11. In the next step the user data columns are selected and load into the database.
12. Now the script calls a SQL query to look up song and artist ID form their tables by song name, artist name and duration of song.
    ```
    song_select = ("""
    SELECT s.song_id, s.artist_id FROM songs s 
    JOIN artists a 
    ON s.artist_id = a.artist_id
    WHERE s.title = %s
    AND a.name = %s
    AND s.duration = %s;
    """)
    ```
13. After the necesarry data is queried the new dataframe is load into the songplays table of the database.

## How to execute the scripts

1. use the python command in the commandline to run the create_table.py script
2. use the python command in the commandline to run the etl.py script
3. All files in the nested folder data should be processed. 

## Files

- **test.ipynb** - displays the first few rows of each table to check the database.
- **create_tables.py** - drops and creates the tables. Run this file to reset the tables before each time the ETL script is executed.
- **etl.ipynb** - reads and processes a single file from song_data and log_data and loads the data into the tables. Contains detailed instructions on the ETL process for each of the tables.
- **etl.py** - reads and processes files from song_data and log_data and loads them into the tables. Contains no instructions on the detailed ETL process
- **sql_queries.py** - contains all sql queries, and is imported into the last three files above.
- **README.md** - provides discussion and explainations on the project.

