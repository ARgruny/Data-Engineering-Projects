# Stock Market Analytics Database
![Top Banner](https://github.com/ARgruny/Data-Engineering-Projects/blob/master/Capstone%20Project/Images/top%20banner.png)

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

### 1. Airflow Instance
For the Airflow instance the following hardware is used:

  `m5.xlarge
  4 vCore, 16 GiB Memory
  Storage: 64 GiB`

The infrastructure can be set up by running the **start_airflow_instance.py** script with

  `python start_airflow_instance.py`

The script uses a YAML file in which the installation and structure of the EC2 instance is described.
The YAML file is hosted in a seperated AWS S3 bucket.
The original file can be found [here](https://s3.amazonaws.com/aws-bigdata-blog/artifacts/airflow.livy.emr/airflow.yaml).

Some parts of the file were changed because they are not needed in this project.
For example the git clone steps to import Airflow DAG's or the download of the Movielens dataset.
The Airflow config file was also changed to set the load example dags variable to **False**.
With this Airflow will be initialized clean without any DAG's

If more input parameters are added to the YAML file, the **start_airflow_instance** script must be updated to address those additional parameters.
To get a better understanding of this, look at the **launch_stack** function in the script.

In addition a **cluster.cfg** file is needed where the aws key and secret will be stored as well as some data for later setup steps corresponding to the Redshift cluster.
**Please keep in mind not to host your actual aws key and secret on github.**

The repository will contain empty YAML and config file for security reasons.
The Script uses the AWS Cloudformation services to set up the Airflow infrastructure.

To start the airflow scheduler connect to the EC2 instance with putty or the command line an use the `$ airflow scheduler` command.

### 2. EMR Cluster
For the EMR cluster the following hardware is used:

  `c5.xlarge
  4 vCore, 8 GiB Memory,
  Storage: 64 GiB`

The cluster can be started by running the **start_emr_cluster.py** script with

  `python start_emr_cluster.py`

The script uses a cluster.cfg file to access the AWS key and secret for authorization. The script was created using the tutorial [here](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-gs.html)
If it is the first time using the AWS EMR service, the default emr roles must be set up before running the script. Otherwise the script will raise an error.

you can use two different approaches:

  1. Use the manual approch by creating a first cluster through the web application
  2. Use the AWS CLI command line and type in `$ aws emr create-default-roles`

To use the AWS CLI Tool you can install it directly from the amazon website [here](https://awscli.amazonaws.com/AWSCLIV2.msi)

### 3. Redshift Cluster
The Redshift cluster has the following hardware

  `dc2.large, 4 Nodes`

Use the two .cfg config files and insert the configuration of the DWH. The `cluster.cfg` is used to start and set up the AWS resources. The `dwh.cfg` file is used for the ETL process. The **start_cluster.py** script will write back into the `dwh.cfg` file so make sure that no field is deleted, even the empty HOST and ARN field.

One script is provided to control the DWH infrstructure. Use the following commands to start up the Redshift cluster

  `python start_cluster.py`

you can change the hardware by changing the number of nodes and the node type in the cluster.cfg file

## Describe and gather Data

### S&P 500 Stock List
A list of stocks with the ticker code of each stock in the S&P 500. The data is from the official [wiki](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies) of the S&P 500.
This extract will be used to query the yahoo finance API and gather most of the data. It contains 505 stocks and represents only a small part of the actual stock market.
But it should be enough to test the infrastructure and ETL pipelines.

#### Data Columns
- Ticker: char code of the stock. this will be used in the yahoo API.
- Name: Name of the Stock
- Sector: Sector or branch of the company
