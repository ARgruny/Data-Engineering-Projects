import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format


config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID']=config.get('AWS', 'AWS_ACCESS_KEY_ID')
os.environ['AWS_SECRET_ACCESS_KEY']=config.get('AWS', 'AWS_SECRET_ACCESS_KEY')


def create_spark_session():
    """
    This function creates/retrieves a spark session
    """
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
    """
    This function loads data from S3, constructs the tables which uses data from the song_data json documents and saves the new tables on S3 again.
    
        Arguments:
        :param spark: spark session object
        :param input_data: string with address to S3 location of song data
        :param output_data: string with address to S3 location for the new tables
        
        :return: None
    """
    # load data from S3
    song_data = input_data + 'song_data/*/*/*/*.json'
    df = spark.read.json(song_data)

    
    # select columns for the songs_table and writes the table to S3
    songs_table = (df.select(
        'song_id', 
        'title', 
        'artist_id', 
        'year', 
        'duration').distinct())
    
    songs_table.write.mode('overwrite').partitionBy('year', 'artist_id').parquet(output_data + 'songs_table/')

    # select columns for the artists_table and writes the table to S3
    artists_table = (df.select(
    'artist_id', 
    col('artist_name').alias('name'),
    col('artist_location').alias('location'),
    col('artist_latitude').alias('latitude'),
    col('artist_longitude').alias('longitude')).distinct())
    
    artists_table.write.parquet(output_data + 'artists/')


def process_log_data(spark, input_data, output_data):
    """
    This function loads data from S3, constructs the table which uses data from the log files and saves the tables on S3
    
        Arguments:
        :param spark: spark session object
        :param input_data: string with address to S3 location of song data
        :param output_data: string with address to S3 location for the new tables
        
        :return: None     
    """
    # load data from S3
    log_data = input_data + 'log_data/*/*/*.json'
    df = spark.read.json(log_data)
    
    # filter by action 'NextSong'
    df = df.filter(df.page == 'NextSong')

    # extract columns for users table and write the table to S3
    users_table = (df.select(
        col('userId').alias('user_id'),
        col('firstName').alias('first_name'),
        col('lastName').alias('last_name'),
        'gender',
        'level').distinct())
    
    users_table.write.mode('overwrite').parquet(output_data + 'users/')

    # create timestamp column from original timestamp column
    df = df.withColumn('timestamp', F.to_timestamp(F.from_unixtime((col('ts') / 1000) , 'yyyy-MM-dd HH:mm:ss.SSS')).cast('Timestamp'))

    # extract columns to create time table and write to S3
    time_table = (
    df.select('timestamp') \
      .withColumn('hour', hour(col('timestamp'))) \
      .withColumn('day', dayofmonth(col('timestamp'))) \
      .withColumn('week', weekofyear(col('timestamp'))) \
      .withcolumn('month', month(col('timestamp'))) \
      .withColumn('year', year(col('timestamp'))) \
      .withColumn('weekday', date_format(col('timestamp'), 'E')))
    
    time_table.write.mode('overwrite').partitionBy('year', 'month').parquet(output_data + 'time/')

    # read in song data and artist data to use for songplays table
    song_df = spark.read.parquet(output_data + 'songs/*/*/*')

    # extract columns to create songplays table and write to S3
    songplays_table = (
    df.withColumn('songplay_id', F.monotonically_increasing_id()) \
      .withColumn('year_session', year(col('timestamp'))) \
      .withColumn('month', month(col('timestamp'))) \
      .join(songs_table, songs_table.title == df.song) \
      .select(
        'songplay_id',
        col('timestamp').alias('start_time'),
        col('userId').alias('user_id'),
        'level',
        'song_id',
        'artist_id',
        col('sessionId').alias('session_id'),
        'location',
        col('userAgent').alias('user_agent'),
        col('year_session').alias('year'),
        'month'))

    songplays_table.write.mode('overwrite').partitionBy('year', 'month').parquet(output_data + 'songplays/')


    
def main():
    spark = create_spark_session()
    input_data = "s3a://udacity-dend/"
    output_data = "s3a://sparkify-agr-dend/"
    
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()
