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

fill_id1 = "42"
fill_id2 = "17"
start_time_fill = datetime.datetime.now() - datetime.timedelta(hours=1)
end_time_fill = datetime.datetime.now() + datetime.timedelta(hours=1)

# Test fill functionality
runDB.add_fill(fill_id=fill_id1, start_time=start_time_fill, end_time=end_time_fill)
runDB.add_fill(fill_id=fill_id2, start_time=start_time_fill, end_time=end_time_fill)
try:
    # IDs have to be unique. The runDB will refuse adding a second fill with the same ID
    runDB.add_fill(fill_id=fill_id2, start_time=start_time_fill, end_time=end_time_fill)
except ValueError:
    pass

# Get a single fill
print(runDB.get_fill(fill_id=fill_id1))
# List all fills (optionally filtering by time window)
print(runDB.list_fills())
print(runDB.list_fills(start_time=start_time_fill, end_time=end_time_fill))
print(runDB.list_fills(start_time=start_time_fill))
print(runDB.list_fills(start_time=end_time_fill))

# Add attributes to a fill
runDB.add_attributes_to_fill(fill_id=fill_id1, energy="6.8 TeV")
# runDB will print a warning and refuse overwriting existing attribute
runDB.add_attributes_to_fill(fill_id=fill_id1, energy="4.8 TeV")
runDB.add_attributes_to_fill(
    fill_id=fill_id1, filling_scheme="single_10b_3_0_0_pilots_7nc_1c"
)
runDB.add_attributes_to_fill(fill_id=fill_id1, B1=1402, B2=1402)
# Result of added attributes
print(runDB.get_fill(fill_id=fill_id1))

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
print(runDB.list_runs(start_time=start_time_fill, end_time=end_time_fill))
print(runDB.list_runs(start_time=start_time_fill))
print(runDB.list_runs(start_time=end_time_fill))
# Test adding attributes to a run
runDB.add_attributes_to_run(run_id=run_id, nb_events=13)
print(runDB.get_run(run_id=run_id))

# Clean up DB
runDB.remove_run(run_id=run_id)
runDB.remove_fill(fill_id=fill_id1)
runDB.remove_fill(fill_id=fill_id2)
