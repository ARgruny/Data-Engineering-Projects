import boto3
import configparser
from botocore.exceptions import ClientError



def get_config_data(file):

    global KEY, SECRET, DWH_CLUSTER_TYPE, DWH_NUM_NODES, \
           DWH_NODE_TYPE, DWH_CLUSTER_IDENTIFIER, DWH_DB, \
           DWH_DB_USER, DWH_DB_PASSWORD, DWH_PORT, DWH_IAM_ROLE_NAME
    
    config = configparser.ConfigParser()
    with open(file) as cfg:
        config.read_file(cfg)

    # Setting up variables
        KEY                    = config.get('AWS','KEY')
        SECRET                 = config.get('AWS','SECRET')
        
        
        
def launch_emr(region, bucket, key_name, subnet):
    
    log_folder = 's3://' + bucket + '/logs'
    
    client = boto3.client('emr', region_name=region, aws_access_key_id=KEY, 
                          aws_secret_access_key=SECRET)
    cluster_id = client.run_job_flow(
            Name='airflow-cluster',
            LogUri=log_folder,
            ReleaseLabel='emr-5.29.0',
            Applications=[
                    {
                        'Name': 'Spark'
                    }
                    ],
            Instances={
                    'InstanceGroups': [
                            {
                                    'Name': 'Master Nodes',
                                    'Market': 'ON_DEMAND',
                                    'InstanceRole': 'MASTER',
                                    'InstanceType': 'c5.xlarge',
                                    'InstanceCount': 1
                            },
                            {
                                    'Name': 'Slave Nodes',
                                    'Market': 'ON_DEMAND',
                                    'InstanceRole': 'CORE',
                                    'InstanceType': 'c5.xlarge',
                                    'InstanceCount': 2
                            }         ],
                    'Ec2KeyName': key_name,
                    'KeepJobFlowAliveWhenNoSteps': True,
                    'TerminationProtected': False,
                    'Ec2SubnetId': subnet
                    },
            VisibleToAllUsers=True,
            JobFlowRole='EMR_EC2_DefaultRole',
            ServiceRole='EMR_DefaultRole',
            )

    
    
    
    
def create_emr_bucket(region, name):
    try:    
        client = boto3.client('s3', region_name=region, aws_access_key_id=KEY, 
                              aws_secret_access_key=SECRET)

        client.create_bucket(Bucket=name)
    except ClientError as e:
        print(e)
        return False
    return True




def main():
    region = 'us-east-1'
    bucket_name = 'airflow-emr-cluster-bucket'
    key_name = 'emr-cluster-key'
    subnet = 'subnet-7cbc3e31' # us-east-1a
    
    # create bucket
    create_emr_bucket(region, bucket_name)
    
    # start emr cluster
    launch_emr(region, bucket_name, key_name, subnet)


if __name__ == '__main__':
    main()
    

