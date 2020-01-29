from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadFactOperator(BaseOperator):

    ui_color = '#F98866'

    @apply_defaults
    def __init__(self,
                 redshift_conn="",
                 aws_creds="",
                 select_query="",
                 table=[],
                 *args, **kwargs):

        super(LoadFactOperator, self).__init__(*args, **kwargs)
        self.redshift_conn = redshift_conn
        self.aws_creds = aws_creds
        self.select_query = select_query
        self.table = table

    def execute(self, context):
        """
        This funtion loads a fact table from the staging tables in redshift
        
            Arguments:
            :param self: self class object
            :param context: context
            
            :return: None
        """
        redshift = PostgresHook(self.redshift_conn)
        redshift.run(f"INSERT INTO {self.table} {self.select_query}")