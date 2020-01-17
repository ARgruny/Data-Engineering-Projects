import configparser
import psycopg2
from sql_queries import create_table_queries, drop_table_queries


def drop_tables(cur, conn):
    """
    drops all tables in the drop_table_queries list
    
        Arguments:
        :param cur: database cursor object
        :param conn: database connection object
        
        :return: None
    """
    for query in drop_table_queries:
        cur.execute(query)
        conn.commit()


        
def create_tables(cur, conn):
    """
    crates all tables in the create_table_queries list
    
        Arguments:
        :param cur: database cursor object
        :param conn: database connection object
        
        :return: None
    """
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()


        
def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')
    
    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    print(conn)
    cur = conn.cursor()

    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()