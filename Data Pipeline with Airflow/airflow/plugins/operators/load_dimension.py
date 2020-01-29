from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadDimensionOperator(BaseOperator):

    ui_color = '#80BD9E'

    @apply_defaults
    def __init__(self,
                 redshift_conn="",
                 table=[],
                 select_query="",
                 truncate=False,
                 *args, **kwargs):

        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        self.redshift_conn = redshift_conn
        self.table = table
        self.select_query = select_query
        self.truncate = truncate

    def execute(self, context):
        """
        This funtion loads a dimension table from the staging tables in redshift
        
            Arguments:
            :param self: self class object
            :param context: context
            
            :return: None
        """
        redshift = PostgresHook(self.redshift_conn)
        if self.truncate:
            redshift.run(f"TRUNCATE TABLE {self.table}")
        filled_sql = self.select_query.format(self.table)
        redshift.run(f"INSERT INTO {self.table} {self.select_query}")
        self.log.info(f"Success: {self.task_id}")
