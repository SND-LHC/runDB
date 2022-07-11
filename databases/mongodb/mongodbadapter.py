"""
This module implements a MongoDB storage back-end adapter.
"""

from json import loads
from datetime import datetime

## As of Python 3.8 we can do more with typing. It is recommended to make
## the adapter class final. Use the following import and provided
## decorator for the class.
from typing import final
from mongoengine import connect, DoesNotExist


# evh add  databases.mongodb.
from databases.mongodb.models.detector import Detector
from databases.mongodb.models.detectorWrapper import DetectorWrapper
from databases.mongodb.models.condition import Condition
from databases.mongodb.models.fill import Fill
from databases.mongodb.models.run import Run
from databases.mongodb.models.file import File
from databases.mongodb.helpers import (
    __sanitize_path,
    __sanitize_str,
    __validate_datetime,
    __validate_interval_parameters,
    __validate_path,
    __validate_str,
    __convert_date,
)

# from databases.mongodb.models.emulsion import Emulsion
# from databases.mongodb.models.brick import Brick

from interface import APIInterface


# Package metadata
__authors__ = [
    "Nathan DPenha",
    "Juan van der Heijden",
    "Vladimir Romashov",
    "Raha Sadeghi",
]
__copyright__ = "TU/e ST2019"
__version__ = "1.0"
__status__ = "Prototype"


def __get_connection(connection_dict):
    """
    Create a connection to a MongoDB server and return the connection handle.
    """
    user = connection_dict["user"]
    password = connection_dict["password"]
    db = connection_dict["db_name"]
    host = connection_dict["host"]
    port = connection_dict["port"]
    # For some reason authentication only works using URI
    uri = f"mongodb://{user}:{password}@{host}:{port}/{db}"
    return connect(host=uri)


@final
class MongoToCDBAPIAdapter(APIInterface):
    """
    Adapter class for a MongoDB back-end that implements the CDB interface.
    """

    # Holds the connection handle to the database
    __db_connection = None

    def __init__(self, connection_dict):
        """
        This constructor makes a connection to the MongoDB conditions DB.

        :param connection_dict: The mongoDB configuration for making the connection
                                to the Conditions Database.
        """
        self.__db_connection = self.__get_connection(connection_dict)

    def __delete_db(self, db_name):
        """
        Delete the specified database.

        :param db_name: The name of the DB that needs to be deleted.
        """
        self.__db_connection.drop_database(db_name)

    def __get_wrapper(self, wrapper_id):
        """
        Returns a DetectorWrapper object. Otherwise it raises a
        ValueError exception if the wrapper_id could not be found.

        :param wrapper_id: String specifying the ID for the wrapper to be returned.
        Must be unique. Must not contain a forward slash (i.e. /).
        """
        if not __validate_str(wrapper_id):
            raise ValueError(
                "Please pass the correct type of the ID for the new detector. "
                "It must be unique, and it must not contain a forward slash "
                "(i.e. /)"
            )

        wrapper_id = __sanitize_path(wrapper_id)
        detector_names = self.__split_detector_names(wrapper_id)

        try:
            detector_wrapper = DetectorWrapper.objects().get(name=detector_names[0])
            return detector_wrapper
        except Exception as e:
            raise ValueError(
                "The detector wrapper ",
                detector_names[0],
                " does not exist in the database",
            ) from e

    def __get_subdetector(self, detector, sub_name):
        """
        Returns a subdetector with name sub_name under the specified parent detector.

        :param detector: Detector object.
        :param sub_name: (String) name of the subdetector that should be returned.
        """
        try:
            subdetector = detector.subdetectors.get(name=sub_name)
        except Exception:
            print("Subdetector " + sub_name + " does not exist")
            return None

        return subdetector

    def __get_detector(self, detector_wrapper, detector_id):
        """
        Returns a Detector object identified by detector_id.
        It raises ValueError if the detector_id could not be found.

        :param detector_wrapper: DetectorWrapper object that contains a detector tree.
        :param detector_id: (String) The ID (i.e. path) to the detector that
        must be retrieved.
        """
        detector_names = self.__split_detector_names(detector_id)
        detector = detector_wrapper.detector
        path = ""

        for i in range(1, len(detector_names)):
            detector = self.__get_subdetector(detector, detector_names[i])
            path = path + "/" + detector_names[i]

            if detector is None:
                path = __sanitize_path(path)
                # evh
                print("The detector " + path + " does not exist in the database")
                # raise ValueError("The detector " +
                #                 path +
                #                 " does not exist in the database")

        return detector

    def __add_wrapper(self, name):
        """
        Creates a new DetectorWrapper object and stores it in the DB.
        Returns this new wrapper or None if a detector with that name
        already exists.

        :param name: (String) uniquely identifying the wrapper.
        """
        if not DetectorWrapper.objects(name=name):
            wrapper = DetectorWrapper()
            wrapper.name = name
            wrapper.save()
            return wrapper
        return None

    def __remove_wrapper(self, wrapper_id):
        """
        Removes a detector wrapper and its contents from the database.

        :param wrapper_id: (String) identifying the wrapper to remove.
        """
        try:
            wrapper = self.__get_wrapper(wrapper_id)
        except Exception:
            # evh
            print("The detector '", wrapper_id, "' does not exist in the database")
            # raise ValueError("The detector '",
            #                 wrapper_id,
            #                 "' does not exist in the database")
        wrapper.delete()

    # Method signature description can be found in the toplevel interface.py file
    def list_detectors(self, parent_id=None):
        detector_list = []

        if not parent_id:
            detector_wrapper_list = DetectorWrapper.objects.all()

            for wrapper in detector_wrapper_list:
                detector_list.append(str(wrapper.detector.name))

        # This executes when a particular parent_id is provided.
        else:
            if not __validate_path(parent_id):
                raise TypeError(
                    "Please pass the correct type of input: parent_id, "
                    "parent_id should be of String type"
                )

            try:
                wrapper = self.__get_wrapper(parent_id)
            except Exception as e:
                raise ValueError(
                    "The detector '", parent_id, "' does not exist in the database"
                ) from e

            detector = self.__get_detector(wrapper, parent_id)
            path = __sanitize_path(parent_id)

            for subdetector in detector.subdetectors:
                detector_list.append(str(path + "/" + subdetector.name))

        return detector_list

    # Method signature description can be found in the toplevel interface.py file
    def get_detector(self, detector_id):
        """
        Get detector
        """
        if detector_id == "":
            raise ValueError(
                "Please specify a valid detector id. A detector id cannot be empty."
            )

        if not __validate_str(detector_id):
            raise TypeError(
                "Please pass the correct type of input: detector_id should be String"
            )

        detector_id = __sanitize_path(detector_id)
        try:
            detector_wrapper = self.__get_wrapper(detector_id)
        except Exception as e:
            raise ValueError(
                "The detector '", detector_id, "' does not exist in the database"
            ) from e

        try:
            detector = self.__get_detector(detector_wrapper, detector_id)
        except Exception as e:
            raise ValueError(
                "The requested detector " + detector_id + " does not exist."
            ) from e

        # Convert the internal Detector object to a generic Python dict type
        return loads(detector.to_json())

    # Method signature description can be found in the toplevel interface.py file
    def list_fills(self, start_date, end_date):
        fill_list = []

        return fill_list

    # Method signature description can be found in the toplevel interface.py file
    # evh to test if a document exists in the db use .objects()
    def get_fill(self, fill_id):
        if fill_id == "":
            raise ValueError(
                "Please specify a valid fill number. A fill number cannot be empty."
            )

        if not __validate_str(fill_id):
            raise TypeError(
                "Please pass the correct type of input: fill_id should be String"
            )

        fill_id = __sanitize_str(fill_id)

        try:
            fill = self.__get_fill(fill_id)
        except Exception as e:
            raise ValueError(
                "The requested fill " + fill_id + " does not exist."
            ) from e

        # Convert the internal Fill object to a generic Python dict type
        return loads(fill.to_json())

    # Method signature description can be found in the toplevel interface.py file
    def get_run(self, run_id):
        if run_id == "":
            raise ValueError(
                "Please specify a valid run number. A run number cannot be empty."
            )

        if not __validate_str(run_id):
            raise TypeError(
                "Please pass the correct type of input: run_id should be String"
            )

        run_id = __sanitize_str(run_id)

        try:
            run = self.__get_run(run_id)
        except Exception as e:
            raise ValueError("The requested run " + run_id + " does not exist.") from e

        # Convert the internal Run object to a generic Python dict type
        return loads(run.to_json())

    # Method signature description can be found in the toplevel interface.py file
    def get_file(self, file_id):
        if file_id == "":
            raise ValueError(
                "Please specify a valid file number. A file number cannot be empty."
            )

        if not __validate_str(file_id):
            raise TypeError(
                "Please pass the correct type of input: file_id should be String"
            )

        file_id = __sanitize_str(file_id)

        try:
            file = self.__get_file(file_id)
        except Exception as e:
            raise ValueError("The requested file" + file_id + " does not exist.") from e

        # Convert the internal File object to a generic Python dict type
        return loads(file.to_json())

    # Method signature description can be found in the toplevel interface.py file
    def get_emulsion(self, emulsion_id):
        if emulsion_id == "":
            raise ValueError(
                "Please specify a valid emulsion number. An emulsion number cannot be empty."
            )

        if not __validate_str(emulsion_id):
            raise TypeError(
                "Please pass the correct type of input: emulsion_id should be String"
            )

        emulsion_id = __sanitize_str(emulsion_id)

        try:
            emulsion = self.__get_file(emulsion_id)
        except Exception as e:
            raise ValueError(
                "The requested emulsion" + emulsion_id + " does not exist."
            ) from e

        # Convert the internal Emulsion object to a generic Python dict type
        return loads(emulsion.to_json())

    # Method signature description can be found in the toplevel interface.py file
    def get_brick(self, brick_id):
        if brick_id == "":
            raise ValueError(
                "Please specify a valid brick number. A brick number cannot be empty."
            )

        if not __validate_str(brick_id):
            raise TypeError(
                "Please pass the correct type of input: brick_id should be String"
            )

        brick_id = __sanitize_str(brick_id)

        try:
            brick = self.__get_file(brick_id)
        except Exception as e:
            raise ValueError(
                "The requested brick" + brick_id + " does not exist."
            ) from e

        # Convert the internal Brick object to a generic Python dict type
        return loads(brick.to_json())

    # Method signature description can be found in the toplevel interface.py file
    def add_fill(self, fill_id, start_time, end_time):
        if fill_id == "":
            raise TypeError("Fill_id should not be empty")

        # Converting all dates given as a String to a datetime object
        if __validate_str(start_time):
            start_time = __convert_date(start_time)
        elif __validate_datetime(valid_until):
            # Strip off the microseconds
            start_time = start_time.replace(microsecond=0)
        if __validate_str(end_time):
            end_time = __convert_date(end_time)
        elif __validate_datetime(end_time):
            # Strip off the microseconds
            end_time = end_time.replace(microsecond=0)

        if start_time > end_time:
            raise ValueError("Incorrect validity interval")

        fill = Fill()
        fill.fill_id = fill_id
        fill.start_time = start_time
        fill.end_time = end_time
        fill.save()

    # Method signature description can be found in the toplevel interface.py file
    def add_run(self, run_id, fill_id, start_time, end_time):
        if run_id == "" or fill_id == "":
            raise TypeError("Run_id or Fill_id should not be empty")

        # Converting all dates given as a String to a datetime object
        if __validate_str(start_time):
            start_time = __convert_date(start_time)
        elif __validate_datetime(valid_until):
            # Strip off the microseconds
            start_time = start_time.replace(microsecond=0)
        if __validate_str(end_time):
            end_time = __convert_date(end_time)
        elif __validate_datetime(end_time):
            # Strip off the microseconds
            end_time = end_time.replace(microsecond=0)

        if start_time > end_time:
            raise ValueError("Incorrect validity interval")

        run = Run()

        run.run_id = run_id
        if get_fill(fill_id) == "":
            raise TypeError("Fill_id " + fill_id + " does not exist.")

        run.fill_id = fill_id
        run.start_time = start_time
        run.end_time = end_time
        run.save()

    # Method signature description can be found in the toplevel interface.py file
    def add_file(self, run_id, file_id, start_time, end_time):
        if run_id == "" or file_id == "":
            raise TypeError("Run_id or File_id should not be empty")

        # Converting all dates given as a String to a datetime object
        if __validate_str(start_time):
            start_time = __convert_date(start_time)
        elif __validate_datetime(valid_until):
            # Strip off the microseconds
            start_time = start_time.replace(microsecond=0)
        if __validate_str(end_time):
            end_time = __convert_date(end_time)
        elif __validate_datetime(end_time):
            # Strip off the microseconds
            end_time = end_time.replace(microsecond=0)

        if start_time > end_time:
            raise ValueError("Incorrect validity interval")

        file = File()

        file.file_id = file_id

        if get_run(run_id) == "":
            raise TypeError("Run_id " + run_id + " does not exist.")

        file.run_id = run_id

        if get_run(fill_id) == "":
            raise TypeError("Fill_id " + fill_id + " does not exist.")

        file.fill_id = fill_id
        file.start_time = start_time
        file.end_time = end_time
        file.save()

    # Method signature description can be found in the toplevel interface.py file
    def remove_fill(self, fill_id):
        if not __validate_str(fill_id):
            raise TypeError(
                "Please pass the correct type of input: fill_id should be String"
            )

        if fill_id == "":
            raise ValueError(
                "Please provide the correct input for fill_id: fill_id cannot be an empty String"
            )

        try:
            fill = self.__get_fill(fill_id)
            fill.remove()
        except Exception:
            # evh
            print("The Fill '", fill_id, "' does not exist in the database")

    # Method signature description can be found in the toplevel interface.py file
    def add_detector(self, name, parent_id=None):
        if not __validate_str(name):
            raise TypeError(
                "Please pass the correct type of input: name should be String"
            )
        # Detector names cannot be empty string
        if name == "":
            raise ValueError(
                "Please pass the correct value of input: name should not "
                "be an empty string"
            )
        # If a / is in the name parameter we raise ValueError Exception
        if "/" in name:
            raise ValueError("The name parameter cannot contain a / ")

        # Remove any unwanted symbols from the name
        name = __sanitize_str(name)

        # This executes when trying to add a root level detector and wrapper
        if parent_id is None or parent_id == "":
            wrapper = self.__add_wrapper(name)

            if wrapper is not None:
                detector = Detector()
                detector.name = name
                wrapper.detector = detector
                wrapper.save()
            # If the wrapper already exist throw an error
            else:
                # evh. should not crash when detector already exists
                print("The detector '", name, "' already exists. Nothing done.")
                # raise ValueError("The detector '" + name + "' already exists")

        # If we add a subdetector
        else:
            if not __validate_path(parent_id):
                raise TypeError(
                    "Please pass the correct type of input: parent_id  "
                    "should be String"
                )

            parent_id = __sanitize_path(parent_id)
            detector_names = self.__split_detector_names(parent_id)

            try:
                detector_wrapper = self.__get_wrapper(detector_names[0])
            except Exception as e:
                raise ValueError(
                    "The detector '",
                    detector_names[0],
                    "' does not exist in the database",
                ) from e

            try:
                detector = self.__get_detector(detector_wrapper, parent_id)
                added_detector = Detector()
                added_detector.name = name
            except Exception as e:
                raise ValueError(
                    "The detector with id '" + parent_id + "' does not exist"
                ) from e

            try:
                detector.subdetectors.get(name=name)
                # evh added this. should not crash if detector already exists.
                print(
                    "Detector '",
                    parent_id,
                    "/",
                    name,
                    "' already exists. Nothing done.",
                )
            except:
                detector.subdetectors.append(added_detector)
                detector_wrapper.save()
            # raise ValueError("Detector '" + parent_id + "/" + name + "' already exist")

    # Method signature description can be found in the toplevel interface.py file
    def remove_detector(self, detector_id):
        if not __validate_str(detector_id):
            raise TypeError(
                "Please pass the correct type of input: detector_id should be String"
            )

        if detector_id == "":
            raise ValueError(
                "Please provide the correct input for detector_id: detector_id "
                "cannot be an empty String"
            )

        detector_id = __sanitize_path(detector_id)

        try:
            wrapper = self.__get_wrapper(detector_id)
        except Exception:
            # evh
            print("The detector '", detector_id, "' does not exist in the database")
            # raise ValueError("The detector '",
            #                 detector_id,
            #                 "' does not exist in the database")

        detector_names = self.__split_detector_names(detector_id)
        # If we want to remove a root detector
        if len(detector_names) < 2:
            try:
                self.__remove_wrapper(detector_names[0])
            except Exception as e:
                raise ValueError(
                    "The detector '",
                    detector_names[0],
                    "' does not exist in the database",
                ) from e

        # Otherwise, when we remove a subdetector
        path = ""

        for i in range(0, len(detector_names) - 1):
            # TODO What's going on here?
            path = path + "/" + detector_names[i]

        path = __sanitize_path(path)
        detector = self.__get_detector(wrapper, path)
        subdetectors = detector.subdetectors

        # Find the subdetector and remove it from the list
        for i, subdetector in enumerate(subdetectors):
            if subdetector.name == detector_names[-1]:
                detector.subdetectors.pop(i)
                break

        wrapper.save()

    # Method signature description can be found in the toplevel interface.py file
    def add_condition(
        self,
        detector_id,
        name,
        tag,
        values,
        condition_type=None,
        collected_at=datetime.now(),  # pylint: disable=no-member
        valid_since=datetime.now(),  # pylint: disable=no-member
        valid_until=datetime.max,  # pylint: disable=no-member
    ):
        if (
            detector_id == ""
            or name == ""
            or tag == ""
            or values == ""
            or values is None
        ):
            raise TypeError(
                "Please pass the correct parameters: parameters detector_id, name, "
                "tag, values should not be empty"
            )

        if not (
            __validate_path(detector_id)
            and __validate_str(tag)
            and __validate_str(name)
        ):
            raise TypeError(
                "Please pass the correct type of input: detector_id, "
                "tag, and name should be String"
            )

        if not (
            (__validate_interval_parameters(valid_since) or valid_since is None)
            and (__validate_interval_parameters(valid_until) or valid_until is None)
            and (__validate_interval_parameters(collected_at) or collected_at is None)
        ):
            raise TypeError(
                "Please pass the correct type of input: valid_since, valid_until and collected_at "
                "should be either String or datetime object"
            )

        if not __validate_str(condition_type) and condition_type is not None:
            raise TypeError(
                "Please pass the correct type of input: type should be String"
            )

        # Converting all dates given as a String to a datetime object
        if __validate_str(valid_until):
            valid_until = __convert_date(valid_until)
        elif __validate_datetime(valid_until):
            # Strip off the microseconds
            valid_until = valid_until.replace(microsecond=0)
        if __validate_str(valid_since):
            valid_since = __convert_date(valid_since)
        elif __validate_datetime(valid_since):
            # Strip off the microseconds
            valid_since = valid_since.replace(microsecond=0)
        if __validate_str(collected_at):
            collected_at = __convert_date(collected_at)
        elif __validate_datetime(collected_at):
            # Strip off the microseconds
            collected_at = collected_at.replace(microsecond=0)

        if valid_since > valid_until:
            raise ValueError("Incorrect validity interval")

        # Get the detector with the specified detector_id
        try:
            detector_wrapper = self.__get_wrapper(detector_id)
        except Exception as e:
            raise ValueError(
                "The detector '", detector_id, "' does not exist in the database"
            ) from e

        detector = None
        try:
            detector = self.__get_detector(detector_wrapper, detector_id)
        except Exception as e:
            raise ValueError(
                "The requested detector '" + detector_id + "' does not exist."
            ) from e

        # Check if this condition already exists in the database
        condition = self.get_condition_by_name_and_tag(detector_id, name, tag)
        if condition is not None:
            raise ValueError("A condition with the same tag '", tag, "' already exists")

        name = __sanitize_str(name)
        tag = __sanitize_str(tag)

        # Create a new condition and associate it to the detector
        condition = Condition()
        condition.name = name
        condition.tag = tag
        condition.values = values
        condition.type = condition_type
        condition.collected_at = collected_at
        condition.valid_until = valid_until
        condition.valid_since = valid_since

        detector.conditions.append(condition)
        detector_wrapper.save()

    # Method signature description can be found in the toplevel interface.py file
    def get_conditions(self, detector_id):
        if not __validate_str(detector_id):
            raise TypeError(
                "Please pass the correct type of input: detector_id should be String"
            )

        try:
            detector_wrapper = self.__get_wrapper(detector_id)
        except Exception as e:
            raise ValueError(
                "The detector '", detector_id, "' does not exist in the database"
            ) from e

        detector = None
        try:
            detector = self.__get_detector(detector_wrapper, detector_id)
        except Exception as e:
            raise ValueError(
                "The requested detector '" + detector_id + "' does not exist."
            ) from e

        conditions_list = []

        # Iterate over all conditions in the detector and append to conditions_list
        for condition in detector.conditions:
            # Convert the internal Condition object(s) to a generic Python dict type
            conditions_list.append(loads(condition.to_json()))

        if conditions_list:
            return conditions_list
        return None

    # Method signature description can be found in the toplevel interface.py file
    def get_conditions_by_name(self, detector_id, name):
        # Input validation
        if not __validate_str(detector_id):
            raise TypeError(
                "Please pass the correct type of input: detector_id should be String"
            )

        if not __validate_str(name):
            raise TypeError(
                "Please pass the correct form of input: name should be String"
            )

        # Input sanitization
        name = __sanitize_str(name)

        # Get the detector of the specified detector_id
        try:
            detector_wrapper = self.__get_wrapper(detector_id)
        except Exception as e:
            raise ValueError(
                "The detector '", detector_id, "' does not exist in the database"
            ) from e

        detector = None
        try:
            detector = self.__get_detector(detector_wrapper, detector_id)
        except Exception as e:
            raise ValueError(
                "The requested detector '" + detector_id + "' does not exist."
            ) from e

        # Query the condition where the 'name' equals the specified name
        conditions = detector.conditions.filter(name=name)
        if not conditions:
            return None

        # Convert the internal Condition object(s) to a generic Python dict type
        condition_dicts = []
        for condition in conditions:
            condition_dicts.append(loads(condition.to_json()))

        return condition_dicts

    # Method signature description can be found in the toplevel interface.py file
    def get_conditions_by_tag(self, detector_id, tag):
        # Input validation
        if not __validate_str(detector_id):
            raise TypeError(
                "Please pass the correct type of input: detector_id should be String"
            )

        if not __validate_str(tag):
            raise TypeError(
                "Please pass the correct format of input: tag should be String"
            )

        # Input sanitization
        tag = __sanitize_str(tag)

        # Get the detector of the specified detector_id
        try:
            detector_wrapper = self.__get_wrapper(detector_id)
        except Exception as e:
            raise ValueError(
                "The detector '", detector_id, "' does not exist in the database"
            ) from e

        detector = None
        try:
            detector = self.__get_detector(detector_wrapper, detector_id)
        except Exception as e:
            raise ValueError(
                "The requested detector '" + detector_id + "' does not exist."
            ) from e

        # Query the condition where the 'tag' equals the specified tag
        conditions = detector.conditions.filter(tag=tag)
        if not conditions:
            return None

        # Convert the internal Condition object(s) to a generic Python dict type
        condition_dicts = []
        for condition in conditions:
            condition_dicts.append(loads(condition.to_json()))

        return condition_dicts

    # Method signature description can be found in the toplevel interface.py file
    def get_conditions_by_name_and_validity(
        self, detector_id, name, start_date, end_date=None
    ):
        # Input validation
        if not __validate_str(detector_id):
            raise TypeError(
                "Please pass the correct type of input: detector_id should be String"
            )

        if not (
            __validate_str(name)
            and __validate_interval_parameters(start_date)
            and (__validate_interval_parameters(end_date) or end_date is None)
        ):
            raise TypeError(
                "Please pass the valid input type: name should be String, "
                "dates could be either datetime or String type."
            )

        # Input sanitization
        name = __sanitize_str(name)

        # Converting all dates given as a String to a datetime object
        if __validate_str(start_date):
            start_date = __convert_date(start_date)
        elif __validate_datetime(start_date):
            start_date = start_date.replace(microsecond=0)  # Strip off the microseconds
        if __validate_str(end_date):
            end_date = __convert_date(end_date)
        elif __validate_datetime(end_date):
            end_date = end_date.replace(microsecond=0)  # Strip off the microseconds

        # Check for a valid interval
        if end_date is not None and start_date is not None:
            if start_date > end_date:
                raise ValueError("Invalid validity interval")

        # Get the detector of the specified detector_id
        try:
            detector_wrapper = self.__get_wrapper(detector_id)
        except Exception as e:
            raise ValueError(
                "The detector '", detector_id, "' does not exist in the database"
            ) from e

        detector = None
        try:
            detector = self.__get_detector(detector_wrapper, detector_id)
        except Exception as e:
            raise ValueError(
                "The requested detector '" + detector_id + "' does not exist."
            ) from e

        # Query the condition where the 'name' equals the specified name
        conditions = detector.conditions.filter(name=name)

        # Loop over all conditions and check whether they are valid within the specified range
        result_list = []
        for condition in conditions:
            # Check if start_date is within the condition validation range
            if condition.valid_since <= start_date <= condition.valid_until:
                # Check if end_date is set
                if end_date is not None:
                    # If end_date is specified it should also be within the condition
                    # validation range
                    if condition.valid_since <= end_date <= condition.valid_until:
                        result_list.append(condition)
                else:
                    result_list.append(condition)

        if not result_list:
            return None

        # Convert the internal Condition object(s) to a generic Python dict type
        condition_dicts = []
        for condition in result_list:
            condition_dicts.append(loads(condition.to_json()))

        return condition_dicts

    # Method signature description can be found in the toplevel interface.py file
    def get_condition_by_name_and_tag(self, detector_id, name, tag):
        # Input validation
        if not __validate_str(detector_id):
            raise TypeError(
                "Please pass the correct type of input: detector_id should be String"
            )

        if not (__validate_str(name) and __validate_str(tag)):
            raise TypeError(
                "Please pass the correct form of input: "
                "name and tag should be String"
            )

        # Input sanitization
        name = __sanitize_str(name)
        tag = __sanitize_str(tag)

        # Get the detector of the specified detector_id
        try:
            detector_wrapper = self.__get_wrapper(detector_id)
        except Exception as e:
            raise ValueError(
                "The detector '", detector_id, "' does not exist in the database"
            ) from e

        try:
            detector = self.__get_detector(detector_wrapper, detector_id)
        except Exception as e:
            raise ValueError(
                "The requested detector '" + detector_id + "' does not exist."
            ) from e

        # Query the condition where the 'name' and 'tag' equal the specified name and tag
        try:
            condition = detector.conditions.get(name=name, tag=tag)
        except DoesNotExist:
            return None

        # Convert the internal Condition object to a generic Python dict type
        return loads(condition.to_json())

    # Method signature description can be found in the toplevel interface.py file
    def get_condition_by_name_and_collection_date(
        self, detector_id, name, collected_at
    ):
        # Input validation
        if not __validate_str(detector_id):
            raise TypeError(
                "Please pass the correct type of input: detector_id should be String"
            )

        if not (__validate_str(name) and __validate_interval_parameters(collected_at)):
            raise TypeError(
                "Please pass the valid input type: name should be String, collected_at could be "
                "either datetime or String type."
            )

        # Input sanitization
        name = __sanitize_str(name)

        # Converting all dates given as a String to a datetime object
        if __validate_str(collected_at):
            collected_at = __convert_date(collected_at)
        elif __validate_datetime(collected_at):
            # Strip off the microseconds
            collected_at = collected_at.replace(microsecond=0)

        # Get the detector of the specified detector_id
        try:
            detector_wrapper = self.__get_wrapper(detector_id)
        except Exception as e:
            raise ValueError(
                "The detector '", detector_id, "' does not exist in the database"
            ) from e

        detector = None
        try:
            detector = self.__get_detector(detector_wrapper, detector_id)
        except Exception as e:
            raise ValueError(
                "The requested detector '" + detector_id + "' does not exist."
            ) from e

        # Query the condition where the 'name' and 'collected_at' equal the specified name and
        # collection_date
        try:
            condition = detector.conditions.get(name=name, collected_at=collected_at)
            # Convert the internal Condition object to a generic Python dict type
            return loads(condition.to_json())
        except DoesNotExist:
            return None

    # Method signature description can be found in the toplevel interface.py file
    def update_condition_by_name_and_tag(
        self,
        detector_id,
        name,
        tag,
        condition_type=None,
        valid_since=None,
        valid_until=None,
    ):
        # Input validation
        if not __validate_str(detector_id):
            raise TypeError(
                "Please pass the correct type of input: detector_id should be String"
            )

        if not (
            (__validate_interval_parameters(valid_since) or valid_since is None)
            and (__validate_interval_parameters(valid_until) or valid_until is None)
            and (__validate_str(condition_type) or condition_type is None)
            and __validate_str(name)
            and __validate_str(tag)
        ):
            raise TypeError(
                "Please pass correct form of input: for valid_since and/or valid_until, "
                "they could be String, datetime or None. Only String is accepted for name, "
                "tag and type."
            )

        # Converting all dates given as a String to a datetime object
        if __validate_str(valid_until):
            valid_until = __convert_date(valid_until)
        elif __validate_datetime(valid_until):
            # Strip off the microseconds
            valid_until = valid_until.replace(microsecond=0)
        if __validate_str(valid_since):
            valid_since = __convert_date(valid_since)
        elif __validate_datetime(valid_since):
            # Strip off the microseconds
            valid_since = valid_since.replace(microsecond=0)

        if valid_until is not None and valid_since is not None:
            if valid_since > valid_until:
                raise ValueError("Invalid validity interval")

        # Input sanitization
        name = __sanitize_str(name)
        tag = __sanitize_str(tag)

        if __validate_str(condition_type):
            condition_type = __sanitize_str(condition_type)

        # Get the detector of the specified detector_id
        try:
            detector_wrapper = self.__get_wrapper(detector_id)
        except Exception as e:
            raise ValueError(
                "The detector '", detector_id, "' does not exist in the database"
            ) from e

        detector = None
        try:
            detector = self.__get_detector(detector_wrapper, detector_id)
        except Exception as e:
            raise ValueError(
                "The requested detector '" + detector_id + "' does not exist."
            ) from e

        condition = None
        try:
            condition = detector.conditions.get(name=name, tag=tag)
        except DoesNotExist as e:
            raise ValueError("No condition with this name and tag can be found") from e

        # Only update fields that are not None
        if type is not None:
            condition.type = condition_type
        if valid_since is not None:
            condition.valid_since = valid_since
        if valid_until is not None:
            condition.valid_until = valid_until

        detector_wrapper.save()
