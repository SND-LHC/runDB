"""Test functionality needed by Thomas.

This is an example file to demonstrate how the runDB API works, using Thomas's example runs
"""
import json
import datetime
import dateutil.parser
from factory import APIFactory

# Instantiate an API factory
api_factory = APIFactory()
# Call construct_DB_API to get an CDB API instance, the path must lead to a
# valid config.yml file containing the database configuration

runDB = api_factory.construct_DB_API("config.yml")

with open("runinfo.json", "r", encoding="utf8") as f:
    runinfodict = json.load(f)

for run_id, run in runinfodict.items():
    print(run_id, run.keys())
    fills = runDB.list_fills()
    fill_id = run["Fillnumber"]
    start_time = dateutil.parser.parse(run["StartTimeC"])
    if fill_id not in fills:
        # Add fill, if necessary
        runDB.add_fill(
            fill_id=fill_id, start_time=start_time, end_time=datetime.datetime.now()
        )
    # Add run
    runDB.add_run(
        run_id=run_id,
        fill_id=fill_id,
        start_time=start_time,
        end_time=start_time + datetime.timedelta(seconds=1),  # make up an end_time
        **run  # Add freeform attributes
    )
    print(runDB.get_run(run_id))
    # Cleanup
    runDB.remove_run(run_id=run_id)
    runDB.remove_fill(fill_id=fill_id)
