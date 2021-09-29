#!/usr/bin/python3
from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

my_dag_id = "dag_load_market"

default_args = {
    'owner': 'tyche',
    'depends_on_past': False,
    'retries': 1,
    'concurrency': 1,
    'schedule_interval': '@once',
}

# dag declaration
dag = DAG(
    dag_id=my_dag_id,
    default_args=default_args,
    start_date=datetime(2019, 6, 17)
)

# generate random users
bash_generate_users = BashOperator(task_id='dag_load_market',
                         bash_command="sh /home/ec2-user/python-virtual-env/env/market_place/execute_market_place.sh",
                         dag=dag)
