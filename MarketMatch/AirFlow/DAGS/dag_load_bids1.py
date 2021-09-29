#!/usr/bin/python3
from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

my_dag_id = "dag_load_bids1"

default_args = {
    'owner': 'tyche',
    'depends_on_past': False,
    'retries': 1,
    'concurrency': 1
}

# dag declaration
dag = DAG(
    dag_id=my_dag_id,
    default_args=default_args,
    start_date=datetime(2019, 6, 17),
    schedule_interval=timedelta(seconds=600)
)

# generate random users
bash_generate_users = BashOperator(task_id='bash_task_generate_users',
                         bash_command="python3 /home/ec2-user/python-virtual-env/env/tyche/generators1/bids/scripts/LoadKinesisUsers.py",
                         dag=dag)

# generate random bids
bash_generate_bids = BashOperator(task_id='bash_task_generate_bids',
                         bash_command="python3 /home/ec2-user/python-virtual-env/env/tyche/generators1/bids/scripts/LoadKinesisBids.py",
                         dag=dag)

# generate random offers
bash_generate_offers = BashOperator(task_id='bash_task_generate_offers',
                         bash_command="python3 /home/ec2-user/python-virtual-env/env/tyche/generators1/bids/scripts/LoadKinesisOffers.py",
                         dag=dag)

bash_generate_users >> bash_generate_bids >> bash_generate_offers