"""This is an example file to demonstrate how the conditionsDatabase API works.

It reads the geometry file and adds subdetectors with their positions to the condDB
Takes about 5 mins to fill the condDB
"""
from argparse import ArgumentParser
from factory import APIFactory


parser = ArgumentParser()
parser.add_argument("-l", "--level", help="TODO", default=0, type=int)
parser.add_argument("-s", "--subdetector", help="TODO", default="SciFi")
options = parser.parse_args()

# Instantiate an API factory
api_factory = APIFactory()
# Call construct_DB_API to get an CDB API instance, the path must lead to a valid config.yml file containing the database configuration

conditionsDB = api_factory.construct_DB_API("config.yml")

detector = ""
count = 0

result = conditionsDB.get_conditions(options.subdetector)
print("Conditions of subdetector ", options.subdetector, " are ", result)
