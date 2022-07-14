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

fill_id1 = "ab2cx4"
fill_id2 = "ab2cx5"
start_time = datetime.datetime.now() - datetime.timedelta(hours=1)
end_time = datetime.datetime.now() + datetime.timedelta(hours=1)
runDB.add_fill(fill_id=fill_id1, start_time=start_time, end_time=end_time)
runDB.add_fill(fill_id=fill_id2, start_time=start_time, end_time=end_time)
try:
    runDB.add_fill(fill_id=fill_id2, start_time=start_time, end_time=end_time)
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
runDB.remove_fill(fill_id=fill_id1)
runDB.remove_fill(fill_id=fill_id2)
