![Top Banner](https://github.com/ARgruny/Data-Engineering-Projects/blob/master/Capstone%20Project/Images/top%20banner.png)


# Stock Market Analytics Database

## Scope of the Project

### Project Overview
Target of this project is to create a database and automated etl pipeline for stock market data from the yahoo finance API and from the new york times API to analyse stock market movement corresponding to articles and news. the data is captured daily to decrease the influence of strong intraday movements of stocks.

### Infrastructure Overview
To create a scalable and stable infrastructure the AWS cloud services will be utilized. All parts of the infrastructure are shown in the graph below:

![Infrastructure](https://github.com/ARgruny/Data-Engineering-Projects/blob/master/Capstone%20Project/Images/infrastructure.png)

The infrastructure will work as follows:
1. An EC2 instance will query the yahoo finance and New York Times API for the raw data.
2. The raw data will be stored in AWS S3 Storage
3. Airflow will be used to schedule and host the ETL pipelines. It will send ETL tasks to an scalable EMR cluster
4. The EMR cluster transforms the data and loads it into Redshift
5. Redshift will function as the data warehouse

To enable a better recreation of the project most steps of setting up the infrastructure are automated vie boto3 and the aws python sdk.

## Infrastructure Setup

### Airflow Instance

For the Airflow instance the following hardware is used:

  m5.xlarge
  4 vCore, 16 GiB Memory
  Storage: 64 GiB

The infrastructure can be set up by running the **start_airflow_instance.py** script with

  python start_airflow_instance.py

The script uses a YAML file in which the installation and structure of the EC2 instance is described. The YAML file is hosted in a seperated AWS S3 bucket.
you can find the original file [here](https://s3.amazonaws.com/aws-bigdata-blog/artifacts/airflow.livy.emr/airflow.yaml)
