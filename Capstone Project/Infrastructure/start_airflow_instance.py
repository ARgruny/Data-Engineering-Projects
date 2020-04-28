import boto3
import configparser


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


def launch_stack(template, region):
  cfn = boto3.client('cloudformation', region_name=region, aws_access_key_id=KEY, aws_secret_access_key=SECRET)
  stackname = 'airflow-stack'
  capabilities = ['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM', 'CAPABILITY_AUTO_EXPAND']
  try:
    stackdata = cfn.create_stack(
      StackName=stackname,
      DisableRollback=True,
      TemplateURL=template,
      Parameters=[
               {
               'ParameterKey': 'KeyName',
               'ParameterValue': 'airflow-web',
               },
               {
               'ParameterKey': 'S3BucketName',
               'ParameterValue': 'airflow-backend-bucket'
               },
               {
               'ParameterKey': 'DBPassword',
               'ParameterValue': 'airflow28082013'
               }
              ],
      Capabilities=capabilities)
    return stackdata
  except Exception as e:
    print(str(e))



def main():
    config_file = 'cluster.cfg'
    get_config_data(config_file)
    template_url = 'https://infrastructure-airflow.s3.eu-central-1.amazonaws.com/airflow.yaml'
    region='us-east-1'
    launch_stack(template_url, region)



if __name__ == '__main__':
    main()
    