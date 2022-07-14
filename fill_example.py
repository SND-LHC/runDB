"""Test runDB functionality.

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

fill_id1 = "ab2cx4"
fill_id2 = "ab2cx5"
start_time_fill = datetime.datetime.now() - datetime.timedelta(hours=1)
end_time_fill = datetime.datetime.now() + datetime.timedelta(hours=1)

# Test fill functionality
runDB.add_fill(fill_id=fill_id1, start_time=start_time_fill, end_time=end_time_fill)
runDB.add_fill(fill_id=fill_id2, start_time=start_time_fill, end_time=end_time_fill)
try:
    runDB.add_fill(fill_id=fill_id2, start_time=start_time_fill, end_time=end_time_fill)
except ValueError:
    pass

fill = runDB.get_fill(fill_id=fill_id1)
print(fill)
runDB.list_fills()
runDB.add_attributes_to_fill(fill_id=fill_id1, energy="6.8 TeV")
runDB.add_attributes_to_fill(fill_id=fill_id1, energy="4.8 TeV")
runDB.add_attributes_to_fill(
    fill_id=fill_id1, filling_scheme="single_10b_3_0_0_pilots_7nc_1c"
)
runDB.add_attributes_to_fill(fill_id=fill_id1, B1=1402, B2=1402)
fill = runDB.get_fill(fill_id=fill_id1)
print(fill)

# Test run functionality
run_id = "1234"
start_time_run = datetime.datetime.now() - datetime.timedelta(hours=0.5)
end_time_run = datetime.datetime.now() + datetime.timedelta(hours=0.5)
runDB.add_run(
    run_id=run_id, fill_id=fill_id1, start_time=start_time_fill, end_time=end_time_fill
)
print(runDB.get_run(run_id=run_id))
print(runDB.list_runs())
print(runDB.list_runs(fill_id=fill_id1))
print(runDB.list_runs(fill_id=fill_id2))
runDB.remove_run(run_id=run_id)
runDB.remove_fill(fill_id=fill_id1)
runDB.remove_fill(fill_id=fill_id2)
