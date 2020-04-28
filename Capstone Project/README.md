![Top Banner](https://github.com/ARgruny/Data-Engineering-Projects/blob/master/Capstone%20Project/Images/top%20banner.png)


# Stock Market Analytics Database

## Open Capstone Project for the Data Engineering Nanodegree

### Project Overview
Target of this project is to create a database and automated etl pipeline for stock market data from the yahoo finance API and from the new york times API to analyse stock market movement corresponding to articles and news. the data is captured daily to decrease the influence of strong intraday movements of stocks.

### Infrastructure
To create a scalable and stable infrastructure the AWS cloud services will be utilized. All parts of the infrastructure are shown in the graph below:

![Infrastructure](https://github.com/ARgruny/Data-Engineering-Projects/blob/master/Capstone%20Project/Images/infrastructure.png)

The infrastructure will work as follows:
1. An EC2 instance will query the yahoo finance and New York Times API for the raw data.
2. The raw data will be stored in AWS S3 Storage
3. Airflow will be used to schedule and host the ETL pipelines. It will send ETL tasks to an scalable EMR cluster
4. the EMR cluster transforms the data and loads it into Redshift
5. Redshift will function as the data warehouse
