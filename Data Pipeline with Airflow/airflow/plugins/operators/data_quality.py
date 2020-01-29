from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 redshift_conn="",
                 tables=[],
                 *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.redshift_conn = redshift_conn
        self.tables = tables

    def execute(self, context):
        """
        This funtion executes some data quality checks
            
            Arguments:
            :param self: self class object
            :param context: context
            
            :return: None
        """
        redshift = PostgresHook(self.redshift_conn)
        for table in self.tables:
            rec = redshift.get_records(f"SELECT COUNT(*) FROM {table}")
            if len(rec) < 1 or len(rec[0]) < 1:
                raise ValueError(f"Data quality check failed. {table} returned no results")
            num_rec = rec[0][0]
            if num_rec < 1:
                raise ValueError(f"Data quality check failed. {table} contained 0 rows")
            self.log.info(f"Data quality on table {table} check passed with {rec[0][0]} records")