## Project Scope
A music streaming startup, Sparkify, has grown their user base and song database even more and want to move their data warehouse to a data lake. Their data resides in S3, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

As their data engineer, you are tasked with building an ETL pipeline that extracts their data from S3, processes them using Spark, and loads the data back into S3 as a set of dimensional tables.

## Data
The data consists of two sources. Song data in json form and log data in json form. The etl.py script access both sources and transforms the data into one fact table and four dimensional tables.
The data can be accessed with the following AWS S3 string addresses:
- `s3a://udacity-dend/song_data/*/*/*/*.json` - containing metadata about songs/artists
- `s3a://udacity-dend/log_data/*/*/*.json` - containing metadata about log events on sparkify

## Files
- `etl.py` - python script which executes the etl process loads the data from AWS S3 transforms the data into tables and writes the tables back to AWS S3.
- `dl.cfg` - config file used to save the AWS credentials for access to AWS S3 Storage.
- `data folder` - contains part of the full data for prototyping with the etl script or completely new scripts.

## Steps to execute the etl script
Fill in the `dl.cfg` with your AWS credentials. This is needed to access the S3 storage. Keep in mind that you have to either change the output S3 bucket to your own or set up a bucket with the same name as the one used in the `etl.py` script. The code can be found in the main function (`output_data = "s3a://sparkify-agr-dend/"`).

Use the `python etl.py` command to execute the script on your local machine. This could take a lot of time. It is better to set up a spark cluster on AWS EMR and start a jupyter notebook in the jupyter lab. 

## Table Specifications

##### Songplay Table

- **title**: songplay_table
- **type**: fact table

| Column | Datatype | Notes |
| ------ | -------- | ----- |
| `songplay_id` | `INTEGER` | primary key and identificator for the table |
| `start_time` | `TIMESTAMP` | timestamp for song |
| `user_id` | `INTEGER` | the user_id associated with the play event of the song |
| `level` | `STRING` | membership level of user |
| `song_id` | `STRING` | identificaor for the played song. This can be null |
| `artist_id` | `STRING` | identificator for the artist of the song. This can not be null |
| `session_id` | `INTEGER` | identificator for the session. |
| `location` | `STRING` | the location from where the event was executed |
| `user_agent` | `STRING` | agent used for the Sparkify app i.e Chrome, Firefox |
| `year` | `INTEGER` | year of the session used to partition the data |
| `month` | `INTEGER` | month of the session used to partition the data |

##### User Table

- **title**: user_table
- **type**: dimension table

| Column | Datatype | Notes |
| ------ | -------- | ----- |
| `user_id` | `INTEGER` | the user_id associated with the play event of the song |
| `first_name` | `STRING` | first name of the user |
| `last_name` | `STRING` | last name of the user |
| `gender` | `STRING` | gender of the user |
| `level` | `STRING` | membership level of user |

##### Song Table

- **title**: song_table
- **type**: dimension table

| Column | Datatype | Notes |
| ------ | -------- | ----- |
| `song_id` | `STRING` | identificaor for the played song |
| `title` | `STRING` | title of the played song. this should not be null as it is the main information about a song |
| `artist_id` | `STRING` | identificator for the artist of the song. we choss this as a distkey as it provides a good distribution (no skewed data) |
| `year` | `INTEGER` | release year of the played song |
| `duration` | `FLOAT` | duration of the played song |

##### Artist Table

- **title**: artists_table
- **type**: dimension table

| Column | Datatype | Notes |
| ------ | -------- | ----- |
| `artist_id` | `STRING` | identificator for the artist of the song |
| `name` | `STRING` | name of the artist |
| `location` | `STRING` | the location from where the event was executed |
| `latitude` | `FLOAT` | The latitude coordinate of the location |
| `longitude` | `FLOAT` | The longitude coordinate of the location |

##### Time Table

- **title**: time_table
- **type**: dimension table

| Column | Datatype | Notes |
| ------ | -------- | ----- |
| `start_time` | `TIMESTAMP` | timestamp for song |
| `hour` | `INTEGER` | The hour from the timestamp  |
| `day` | `INTEGER` | The day of the month from the timestamp |
| `week` | `INTEGER` | The week of the year from the timestamp |
| `month` | `INTEGER` | The month of the year from the timestamp |
| `year` | `INTEGER` | The year from the timestamp |
| `weekday` | `STRING` | first three letters of the week day from the timestamp |
