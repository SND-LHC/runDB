"""Test run functionality.

This is an example file to demonstrate how the conditionsDatabase API works
"""
from argparse import ArgumentParser
import datetime
from factory import APIFactory

parser = ArgumentParser()
options = parser.parse_args()

# Instantiate an API factory
api_factory = APIFactory()
# Call construct_DB_API to get an CDB API instance, the path must lead to a
# valid config.yml file containing the database configuration

runDB = api_factory.construct_DB_API("config.yml")

fill_id = "123"
run_id = "1234"
start_time_fill = datetime.datetime.now() - datetime.timedelta(hours=1)
end_time_fill = datetime.datetime.now() + datetime.timedelta(hours=1)
start_time_run = datetime.datetime.now() - datetime.timedelta(hours=0.5)
end_time_run = datetime.datetime.now() + datetime.timedelta(hours=0.5)
runDB.add_fill(fill_id=fill_id, start_time=start_time_fill, end_time=end_time_fill)
runDB.add_run(
    run_id=run_id, fill_id=fill_id, start_time=start_time_fill, end_time=end_time_fill
)
print(runDB.get_run(run_id=run_id))
print(runDB.list_runs())
print(runDB.list_runs(fill_id=fill_id))
print(runDB.list_runs(fill_id="145"))
runDB.remove_run(run_id=run_id)
runDB.remove_fill(fill_id=fill_id)
