"""List detectors.

This is an example file to demonstrate how the conditionsDatabase API works
It reads the geometry file and adds subdetectors with their positions to the condDB
Takes about 5 mins to fill the condDB
"""
from argparse import ArgumentParser
import datetime
from factory import APIFactory

parser = ArgumentParser()
# parser.add_argument("-l", "--level", help="TODO", required=True, type=int)
options = parser.parse_args()

# Instantiate an API factory
api_factory = APIFactory()
# Call construct_DB_API to get an CDB API instance, the path must lead to a
# valid config.yml file containing the database configuration

runDB = api_factory.construct_DB_API("config.yml")

fill_id = "ab2cx4"
start_time = datetime.datetime.now() - datetime.timedelta(hours=1)
end_time = datetime.datetime.now() + datetime.timedelta(hours=1)
runDB.add_fill(fill_id=fill_id, start_time=start_time, end_time=end_time)

fill = runDB.get_fill(fill_id=fill_id)
print(fill)
fill = runDB.remove_fill(fill_id=fill_id)
