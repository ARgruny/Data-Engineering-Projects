# Importing Libaries
import pandas as pd
import boto3
import json
import configparser
import time

KEY                    = None
SECRET                 = None
DWH_CLUSTER_TYPE       = None
DWH_NUM_NODES          = None
DWH_NODE_TYPE          = None
DWH_CLUSTER_IDENTIFIER = None
DWH_DB                 = None
DWH_DB_USER            = None
DWH_DB_PASSWORD        = None
DWH_PORT               = None
DWH_IAM_ROLE_NAME      = None


def get_config_data(file):
    """
    This function open a aws dhw config file and read the variables (Global)
    
        Arguments:
        :param file: Str with filename
        
        :return: None
    """
    global KEY, SECRET, DWH_CLUSTER_TYPE, DWH_NUM_NODES, \
           DWH_NODE_TYPE, DWH_CLUSTER_IDENTIFIER, DWH_DB, \
           DWH_DB_USER, DWH_DB_PASSWORD, DWH_PORT, DWH_IAM_ROLE_NAME
    
    config = configparser.ConfigParser()
    with open(file) as cfg:
        config.read_file(cfg)

    # Setting up variables
        KEY                    = config.get('AWS','KEY')
        SECRET                 = config.get('AWS','SECRET')
        DWH_CLUSTER_TYPE       = config.get("DWH","DWH_CLUSTER_TYPE")
        DWH_NUM_NODES          = config.get("DWH","DWH_NUM_NODES")
        DWH_NODE_TYPE          = config.get("DWH","DWH_NODE_TYPE")
        DWH_CLUSTER_IDENTIFIER = config.get("DWH","DWH_CLUSTER_IDENTIFIER")
        DWH_DB                 = config.get("DWH","DWH_DB")
        DWH_DB_USER            = config.get("DWH","DWH_DB_USER")
        DWH_DB_PASSWORD        = config.get("DWH","DWH_DB_PASSWORD")
        DWH_PORT               = config.get("DWH","DWH_PORT")
        DWH_IAM_ROLE_NAME      = config.get("DWH", "DWH_IAM_ROLE_NAME")

        
def set_resource(name, region):
    """
    Sets up the aws resource defined by name and region
    
        Arguments:
        :param name: Str, Name of resource
        :param region: Str, Name of Region
        
        :return: boto3 resource object
    """
    global KEY, SECRET
    return boto3.resource(name, region_name=region, aws_access_key_id=KEY,  aws_secret_access_key=SECRET)


        
def set_client(service, region):
    """
    Sets up the aws client defined by name and region
    
        Arguments:
        :param service: Str, Name of service
        :param region: Str, Name of region
        
        :return: boto3 client object
    """
    global KEY, SECRET
    return boto3.client(service, region_name=region, aws_access_key_id=KEY, aws_secret_access_key=SECRET)



def create_role(iam):
    """
    Creates an AWS IAM Role
    
        Arguments:
        :param iam: boto3 iam client object
        
        :return: boto3 role object
    """
    global DWH_IAM_ROLE_NAME
    dwhRole = None
    try:
        print('Start Creating a new IAM Role...')
        dwhRole = iam.create_role(
            Path='/',
            RoleName=DWH_IAM_ROLE_NAME,
            Description = "Allows Redshift clusters to call AWS services on your behalf.",
            AssumeRolePolicyDocument=json.dumps(
                {'Statement': [{'Action': 'sts:AssumeRole',
                   'Effect': 'Allow',
                   'Principal': {'Service': 'redshift.amazonaws.com'}}],
                 'Version': '2012-10-17'})
        )    
    except Exception as e:
        print('')
        print(e)
        dwhRole = iam.get_role(RoleName=DWH_IAM_ROLE_NAME)
    return dwhRole



def attach_policy(iam):
    """
    Ataches the defined policy to the IAM role
        
        Arguments:
        :param iam: boto3 iam client
        :param policy: Str, Name of policy
        
        :return: Str, HTML status response
    """
    global DWH_IAM_ROLE_NAME
    print('Attaching policy to role...')
    policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess" 
    response = iam.attach_role_policy(RoleName=DWH_IAM_ROLE_NAME, PolicyArn=policy_arn)['ResponseMetadata']['HTTPStatusCode']
    return response



def get_iam_role(iam):
    """
    Gets the ARN string of the role
        
        Arguments:
        :param iam: boto3 iam client
        
        :return: str of the role ARN
    """
    global DWH_IAM_ROLE_NAME
    return iam.get_role(RoleName=DWH_IAM_ROLE_NAME)['Role']['Arn']



def start_cluster(redshift, roleArn):
    """
    This function starts a AWS redshift cluster
    
        Arguments:
        :param redshift: boto3 resource client
        :param roleArn: str of role ARN
        
        :return: boolean, True if succesful else False
    """
    global DWH_CLUSTER_TYPE, DWH_NODE_TYPE, DWH_NUM_NODES, \
           DWH_DB, DWH_CLUSTER_IDENTIFIER, DWH_DB_USER, DWH_DB_PASSWORD
    print('Starting the cluster...')
    try:
        response = redshift.create_cluster(        
            #HW
            ClusterType=DWH_CLUSTER_TYPE,
            NodeType=DWH_NODE_TYPE,
            NumberOfNodes=int(DWH_NUM_NODES),

            #Identifiers & Credentials
            DBName=DWH_DB,
            ClusterIdentifier=DWH_CLUSTER_IDENTIFIER,
            MasterUsername=DWH_DB_USER,
            MasterUserPassword=DWH_DB_PASSWORD,
        
            #Roles (for s3 access)
            IamRoles=[roleArn]  
        )
        print('Redshift HTTP response status code: ')
        print(response['ResponseMetadata']['HTTPStatusCode'])
        return response['ResponseMetadata']['HTTPStatusCode'] == 200
    except Exception as e:
        print(e)
    return False



def create_redshift_port(ec2, redshift):
    """
    Opens port on security group
    
        Arguments:
        :param ec2: boto3 ec2 client
        :param redshift: boto3 redshift client
        
        :return: None
    """
    global DWH_CLUSTER_IDENTIFIER, DWH_PORT
    ClusterProps = redshift.describe_clusters(ClusterIdentifier=DWH_CLUSTER_IDENTIFIER)['Clusters'][0]
    try:
        vpc = ec2.Vpc(id=ClusterProps['VpcId'])
        defaultSg = list(vpc.security_groups.all())[0]
        print(defaultSg)
    
        defaultSg.authorize_ingress(
            GroupName=defaultSg.group_name,
            CidrIp='0.0.0.0/0',
            IpProtocol='TCP',
            FromPort=int(DWH_PORT),
            ToPort=int(DWH_PORT))
        print('')
        print('Successful setting up EC2')
    except Exception as e:
        print(e)



def check_cluster_status(redshift):
    """
    retrieves actual satatus of a redshift cluster
    
        Arguments:
        :param redshift: boto3 redshift client
        
        :return: boolean, True if cluster is available else False
    """
    global DWH_CLUSTER_IDENTIFIER
    ClusterProps = redshift.describe_clusters(ClusterIdentifier=DWH_CLUSTER_IDENTIFIER)['Clusters'][0]
    status = ClusterProps['ClusterStatus'].lower()
    if status == 'available':
        return True
    return False
        


def write_host_info(redshift, file):
    """
    gets the Host and ARN info from cluster and writes back into config file
    
        Arguments:
        
        :param redhsift: boto3 redshift client
        
        :return: None
    """
    global DWH_CLUSTER_IDENTIFIER
    ClusterProps = redshift.describe_clusters(ClusterIdentifier=DWH_CLUSTER_IDENTIFIER)['Clusters'][0]
    
    config = configparser.ConfigParser()
    
    with open(file) as configfile:
        config.read_file(configfile)
    
    config.set("CLUSTER", "HOST", ClusterProps['Endpoint']['Address'])
    config.set("IAM_ROLE", "ARN", ClusterProps['IamRoles'][0]['IamRoleArn'])
    
    with open(file, 'w+') as configfile:
        config.write(configfile)



def terminate_cluster(redshift):
    """
    deletes redshift cluster
        
        Arguments:
        :param redshift: boto3 redshift client
        
        :return: None
    """
    global DWH_CLUSTER_IDENTIFIER
    redshift.delete_cluster(ClusterIdentifier=DWH_CLUSTER_IDENTIFIER, SkipFinalClusterSnapshot=True)
    
    
    
    
def detach_role(iam):
    """
    detaches set roles and policies
    
        Arguments:
        :param iam: boto3 iam client
        
        :return: None
    """
    global DWH_IAM_ROLE_NAME
    iam.detach_role_policy(RoleName=DWH_IAM_ROLE_NAME, PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess")
    iam.delete_role(RoleName=DWH_IAM_ROLE_NAME)
        
        
        
def main():
    
    # setting up variables
    get_config_data('cluster.cfg')
    
    # creating clients & resources
    iam = set_client('iam', 'us-west-2')
    redshift = set_client('redshift', 'us-west-2')
    ec2 = set_resource('ec2', 'us-west-2')
    
    # set role & attch policy
    create_role(iam)
    attach_policy(iam)
    roleArn = get_iam_role(iam)
    
    # start the cluster
    cluster_creation_response = start_cluster(redshift, roleArn)
    
    # wait till cluster runs. (for loop waits max 5Min)
    for i in range(20):
        if check_cluster_status(redshift) == True:
            print('Cluster is available!')
            print('Opening ports to cluster...')
            create_redshift_port(ec2, redshift)
            break
        else:
            time.sleep(30)
    
    print('Cluster creation done!')
    
    # get host and write back in .cfg file
    write_host_info(redshift, 'dwh.cfg')
    
if __name__ == '__main__':
    main()
    
    