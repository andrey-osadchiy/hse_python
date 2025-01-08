from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
 
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}
 
def extract_data_from_postgres():
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    sql = """
    SELECT 
      pc."name" as category_name,
      COUNT(DISTINCT o.user_id) as cnt_u_id,
      SUM(od.quantity) as all_quantity,
      SUM(od.total_price) as total_price 
    FROM orders o 
    JOIN orderdetails od ON o.order_id = od.order_id 
    JOIN products p ON p.product_id = od.product_id 
    JOIN productcategories pc ON p.category_id = pc.category_id 
    GROUP BY pc."name";
    """
    connection = postgres_hook.get_conn()
    cursor = connection.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results
 
def load_data_to_mysql(ti):
    data = ti.xcom_pull(task_ids='extract_data_from_postgres')
    if not data:
        raise ValueError("No data fetched from PostgreSQL.")
 
    mysql_hook = MySqlHook(mysql_conn_id='mysql_default')
    sql = """
    REPLACE INTO category_summary (
      category_name,
      cnt_u_id,
      all_quantity,
      total_price
    ) VALUES (%s, %s, %s, %s);
    """
    connection = mysql_hook.get_conn()
    cursor = connection.cursor()
    cursor.executemany(sql, data)
    connection.commit()
    cursor.close()
    connection.close()
 
with DAG(
    dag_id='postgres_to_mysql',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=datetime(2025, 1, 1),
    catchup=False,
) as dag:
 
    extract_task = PythonOperator(
        task_id='extract_data_from_postgres',
        python_callable=extract_data_from_postgres,
    )
 
    load_task = PythonOperator(
        task_id='load_data_to_mysql',
        python_callable=load_data_to_mysql,
    )
 
    extract_task >> load_task