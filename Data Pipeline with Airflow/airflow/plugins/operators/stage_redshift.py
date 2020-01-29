from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class StageToRedshiftOperator(BaseOperator):
    
    ui_color = '#358140'

    copy_query = """
        COPY {}
        FROM '{}'
        ACCESS_KEY_ID '{}'
        SECRET_ACCESS_KEY '{}'
        COMPUPDATE OFF STATUPDATE OFF
        FORMAT AS JSON '{}';
    """

    @apply_defaults
    def __init__(self,
                 redshift_conn="",
                 aws_creds="",
                 table=[],
                 s3_bucket="",
                 s3_key="",
                 json_path="auto",
                 *args, **kwargs):

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        self.redshift_conn = redshift_conn
        self.aws_creds = aws_creds
        self.table = table
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.json_path = json_path
        self.execution_date = kwargs.get("execution_date")

    def execute(self, context):
        """
        loads the data from aws s3 to the staging tables in redshift
        
            Arguments:
            :param self: self class object
            :param context: context for the s3 connection
            
            :return: None
        """
        aws = AwsHook(self.aws_creds)
        creds = aws.get_credentials()
        redshift = PostgresHook(self.redshift_conn)
        
        self.log.info("deletes from destination table")
        redshift.run("DELETE FROM {}".format(self.table))
        
        self.log.info("loading data from s3 to redshift")
        rend_key = self.s3_key.format(**context)
        s3_path = "s3://{}/{}".format(self.s3_bucket, rend_key)
        filled_sql = StageToRedshiftOperator.copy_query.format(
            self.table,
            s3_path,
            creds.access_key,
            creds.secret_key,
            self.json_path)
        
        redshift.run(filled_sql)