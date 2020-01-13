## Project Context

A startup called Sparkify wants to analyze the data they've been collecting on songs and user activity on their new music streaming app. The analysis team is particularly interested in understanding what songs users are listening to. Currently, there is no easy way to query the data to generate the results, since the data reside in a directory of CSV files on user activity on the app.

Target for Sparkify is to create a Apache Cassandra database with the necesarry tables for the analysis.

## Data

The data is provided through csv files in the folder event_data. All csv files are processed into one csv file containing the necesarry data for the project.

## Files

The project contains the following files:
- **event_datafile_new**: processed .csv file with the necesarry data.
- **Project_1B_Project_Template**: A Jupyter Notebook file containing all steps to process the csv files an all steps for the ETL pipeline
- **event_data folder**: Folder containing the smaller csv files

## Project Steps

Steps taken in the ETL Pipeline:
1. Script to process each csv file in the event_data folder and create a new event_data file.
2. Create a Cassandra Cluster
3. Create a Cassandra Keyspace and set the Keyspace
4. Analyse the data and model the tables according to future queries. 
5. Define the Create Table statements. 
6. Insert the data into the created tables.
7. Define the Select statements for the queries and execute them.
8. Read the data from the queries into a pandas Dataframe. 
9. Close the sessions