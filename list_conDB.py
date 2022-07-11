"""
List detectors

This is an example file to demonstrate how the conditionsDatabase API works
It reads the geometry file and adds subdetectors with their positions to the condDB
Takes about 5 mins to fill the condDB
"""
from argparse import ArgumentParser
from factory import APIFactory

parser = ArgumentParser()
parser.add_argument("-l", "--level", help="TODO", required=True, type=int)
options = parser.parse_args()

# Instantiate an API factory
api_factory = APIFactory()
# Call construct_DB_API to get an CDB API instance, the path must lead to a valid config.yml file containing the database configuration

conditionsDB = api_factory.construct_DB_API("config.yml")

DETECTOR = ""
COUNT = 0


def showdetectors(detector, count, level):
    """
    Show all detector names in the database:
    """
    result = conditionsDB.list_detectors(detector)
    for sd in result:
        if detector == "":
            print("snd subdetectors:", sd)
            conditions = conditionsDB.get_conditions_by_tag(sd, "Scifi_1")
            print("conditions of detector", sd, " :", conditions)
        else:
            print("subdetectors inside", detector, " :", result)
        if count < level:
            count += 1
            for j in range(len(result)):
                showdetectors(result[j], count, level)
    else:
        print("No more subdetectors below subdetector/channel:", detector)


showdetectors(DETECTOR, COUNT, options.level)
