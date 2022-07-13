"""This module implements a MongoDB storage back-end adapter."""
import atexit

from json import loads
from datetime import datetime

## As of Python 3.8 we can do more with typing. It is recommended to make
## the adapter class final. Use the following import and provided
## decorator for the class.
from typing import final
from mongoengine import connect, DoesNotExist, disconnect


from databases.mongodb.models.detector import Detector
from databases.mongodb.models.detectorWrapper import DetectorWrapper
from databases.mongodb.models.condition import Condition
from databases.mongodb.models.fill import Fill
from databases.mongodb.models.run import Run
from databases.mongodb.models.file import File
from databases.mongodb.helpers import (
    sanitize_path,
    sanitize_str,
    validate_datetime,
    validate_interval_parameters,
    validate_path,
    validate_str,
    convert_date,
    split_detector_names,
    create_uri,
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


def get_connection(connection_dict):
    """Create a connection to a MongoDB server and return the connection handle."""
    # For some reason authentication only works using URI
    return connect(host=create_uri(connection_dict))


@final
class MongoToCDBAPIAdapter(APIInterface):
    """Adapter class for a MongoDB back-end that implements the CDB interface."""

    # Holds the connection handle to the database
    __db_connection = None

    def __init__(self, connection_dict):
        """Connect to the MongoDB conditions DB.

        :param connection_dict: The mongoDB configuration for making the connection
                                to the Conditions Database.
        """
        self.__db_connection = get_connection(connection_dict)
        atexit.register(disconnect)

    def __delete_db(self, db_name):
        """Delete the specified database.

        :param db_name: The name of the DB that needs to be deleted.
        """
        self.__db_connection.drop_database(db_name)

    def __get_wrapper(self, wrapper_id):
        """Return a DetectorWrapper object.

        Otherwise it raises a ValueError exception if the wrapper_id could not be found.

        :param wrapper_id: String specifying the ID for the wrapper to be returned.
        Must be unique. Must not contain a forward slash (i.e. /).
        """
        if not validate_str(wrapper_id):
            raise ValueError(
                "Please pass the correct type of the ID for the new detector. "
                "It must be unique, and it must not contain a forward slash "
                "(i.e. /)"
            )

        wrapper_id = sanitize_path(wrapper_id)
        detector_names = split_detector_names(wrapper_id)

        try:
            detector_wrapper = DetectorWrapper.objects().get(name=detector_names[0])
            return detector_wrapper
        except DoesNotExist as e:
            raise ValueError(
                "The detector wrapper ",
                detector_names[0],
                " does not exist in the database",
            ) from e

    def __get_subdetector(self, detector, sub_name):
        """Return a subdetector with name sub_name under the specified parent detector.

        :param detector: Detector object.
        :param sub_name: (String) name of the subdetector that should be returned.
        """
        try:
            subdetector = detector.subdetectors.get(name=sub_name)
        except DoesNotExist:
            print("Subdetector " + sub_name + " does not exist")
            return None

        return subdetector

    def __get_detector(self, detector_wrapper, detector_id):
        """Return a Detector object identified by detector_id.

        It raises ValueError if the detector_id could not be found.

        :param detector_wrapper: DetectorWrapper object that contains a detector tree.
        :param detector_id: (String) The ID (i.e. path) to the detector that
        must be retrieved.
        """
        detector_names = split_detector_names(detector_id)
        detector = detector_wrapper.detector
        path = ""

        for detector_name in detector_names[1:]:
            detector = self.__get_subdetector(detector, detector_name)
            path = path + "/" + detector_name

            if detector is None:
                path = sanitize_path(path)
                raise ValueError(
                    "The detector " + path + " does not exist in the database"
                )

        return detector

    def __add_wrapper(self, name):
        """Create a new DetectorWrapper object and stores it in the DB.

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
        """Remove a detector wrapper and its contents from the database.

        :param wrapper_id: (String) identifying the wrapper to remove.
        """
        try:
            wrapper = self.__get_wrapper(wrapper_id)
        except ValueError as e:
            raise ValueError(
                "The detector '", wrapper_id, "' does not exist in the database"
            ) from e
        wrapper.delete()

    def list_detectors(self, parent_id=None):
        """Return a list with all the detector names in the database.

        @param detector_id:     (optional) String identifying the parent detector to
                                retrieve the (sub)detector names for
                                (i.e. 'muonflux/driftTubes').
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If parent_id does not exist.
        @retval List:           A list with (string) names of detectors under the specified parent.
        """
        detector_list = []

        if not parent_id:
            detector_wrapper_list = DetectorWrapper.objects.all()

            for wrapper in detector_wrapper_list:
                detector_list.append(str(wrapper.detector.name))

        # This executes when a particular parent_id is provided.
        else:
            if not validate_path(parent_id):
                raise TypeError(
                    "Please pass the correct type of input: parent_id, "
                    "parent_id should be of String type"
                )

            try:
                wrapper = self.__get_wrapper(parent_id)
            except ValueError as e:
                raise ValueError(
                    "The detector '", parent_id, "' does not exist in the database"
                ) from e

            detector = self.__get_detector(wrapper, parent_id)
            path = sanitize_path(parent_id)

            for subdetector in detector.subdetectors:
                detector_list.append(str(path + "/" + subdetector.name))

        return detector_list

    def get_detector(self, detector_id):
        """Return a detector dictionary.

        @param  detector_id:    String identifying the detector to retrieve
                                (i.e. 'muonflux/driftTubes').
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If detector_id does not exist.
        @retval Dict:           A dictionary adhering to the following specification:
                                Detector = { 'name': String, 'subdetectors': List of Detector,
                                            'conditions': List of Condition }
        """
        if detector_id == "":
            raise ValueError(
                "Please specify a valid detector id. A detector id cannot be empty."
            )

        if not validate_str(detector_id):
            raise TypeError(
                "Please pass the correct type of input: detector_id should be String"
            )

        detector_id = sanitize_path(detector_id)
        try:
            detector_wrapper = self.__get_wrapper(detector_id)
        except DoesNotExist as e:
            raise ValueError(
                "The detector '", detector_id, "' does not exist in the database"
            ) from e

        try:
            detector = self.__get_detector(detector_wrapper, detector_id)
        except ValueError as e:
            raise ValueError(
                "The requested detector " + detector_id + " does not exist."
            ) from e

        # Convert the internal Detector object to a generic Python dict type
        return loads(detector.to_json())

    def list_fills(self, start_date, end_date):
        """Return a list with fill numbers of all fills in the database.

        @param  start_date:     Timestamp specifying a start of a date/time range for which
                                conditions must be valid.
                                Can be of type String or datetime.
        @param  end_date:       (optional) Timestamp specifying the end of a date/time range for
                                which conditions must be valid.
                                If not specified then we will query for validity on the start_date.
                                Can be of type String or datetime
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:
        @retval List:           A list with (string) fill numbers
        """
        fill_list = []

        return fill_list

    def get_fill(self, fill_id):
        """Return a fill dictionary.

        @param  fill_id:        String identifying the fill to retrieve
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If fill_id does not exist.
        @retval Dict:           A dictionary adhering to the following specification:
                                Fill = { 'Fill_number': String, 'Start_time': datetime, 'End_time': datetime,
                                             'Attributes': List of Attributes }
        """
        if fill_id == "":
            raise ValueError(
                "Please specify a valid fill number. A fill number cannot be empty."
            )

        if not validate_str(fill_id):
            raise TypeError(
                "Please pass the correct type of input: fill_id should be String"
            )

        fill_id = sanitize_str(fill_id)

        try:
            fill = self.__get_fill(fill_id)
        except Exception as e:
            raise ValueError(
                "The requested fill " + fill_id + " does not exist."
            ) from e

        # Convert the internal Fill object to a generic Python dict type
        return loads(fill.to_json())

    def get_run(self, run_id):
        """Return a run dictionary.

        @param  run_id:         String identifying the run to retrieve
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If run_id does not exist.
        @retval Dict:           A dictionary adhering to the following specification:
                                Run = { 'Run_number': String, 'Start_time': datetime, 'End_time': datetime,
                                            'Attributes': List of Attributes }
        """
        if run_id == "":
            raise ValueError(
                "Please specify a valid run number. A run number cannot be empty."
            )

        if not validate_str(run_id):
            raise TypeError(
                "Please pass the correct type of input: run_id should be String"
            )

        run_id = sanitize_str(run_id)

        try:
            run = self.__get_run(run_id)
        except Exception as e:
            raise ValueError("The requested run " + run_id + " does not exist.") from e

        # Convert the internal Run object to a generic Python dict type
        return loads(run.to_json())

    def get_file(self, file_id):
        """Return a file dictionary.

        @param  file_id:        String identifying the file to retrieve
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If file_id does not exist.
        @retval Dict:           A dictionary adhering to the following specification:
                                File = { 'Path': String, 'Start_time': datetime, 'End_time': datetime,
                                            'Attributes': List of Attributes }
        """
        if file_id == "":
            raise ValueError(
                "Please specify a valid file number. A file number cannot be empty."
            )

        if not validate_str(file_id):
            raise TypeError(
                "Please pass the correct type of input: file_id should be String"
            )

        file_id = sanitize_str(file_id)

        try:
            file = self.__get_file(file_id)
        except Exception as e:
            raise ValueError("The requested file" + file_id + " does not exist.") from e

        # Convert the internal File object to a generic Python dict type
        return loads(file.to_json())

    def get_emulsion(self, emulsion_id):
        """Return an emulsion dictionary.

        @param  emulsion_id:    String identifying the emulsion to retrieve
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If emulsion_id does not exist.
        @retval Dict:           A dictionary adhering to the following specification:
                                File = { 'Emulsion_id': String, 'Start_time': datetime, 'End_time': datetime,
                                             'Attributes': List of Attributes }
        """
        if emulsion_id == "":
            raise ValueError(
                "Please specify a valid emulsion number. An emulsion number cannot be empty."
            )

        if not validate_str(emulsion_id):
            raise TypeError(
                "Please pass the correct type of input: emulsion_id should be String"
            )

        emulsion_id = sanitize_str(emulsion_id)

        try:
            emulsion = self.__get_file(emulsion_id)
        except Exception as e:
            raise ValueError(
                "The requested emulsion" + emulsion_id + " does not exist."
            ) from e

        # Convert the internal Emulsion object to a generic Python dict type
        return loads(emulsion.to_json())

    def get_brick(self, brick_id):
        """Return an brick dictionary.

        @param  brick_id:       String identifying the brick to retrieve
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If fill_id does not exist.
        @retval Dict:           A dictionary adhering to the following specification:
                                Brick = { 'Brick_id': String, 'Start_time': datetime, 'End_time': datetime,
                                             'Attributes': List of Attributes }
        """
        if brick_id == "":
            raise ValueError(
                "Please specify a valid brick number. A brick number cannot be empty."
            )

        if not validate_str(brick_id):
            raise TypeError(
                "Please pass the correct type of input: brick_id should be String"
            )

        brick_id = sanitize_str(brick_id)

        try:
            brick = self.__get_file(brick_id)
        except Exception as e:
            raise ValueError(
                "The requested brick" + brick_id + " does not exist."
            ) from e

        # Convert the internal Brick object to a generic Python dict type
        return loads(brick.to_json())

    def add_fill(self, fill_id, start_time, end_time):
        """Add a new fill to the database.

        @param  fill_id:        String specifying the fill number. Must
                                be unique. Must not contain a forward slash (i.e. /).
        @param  start_time:     Timestamp specifying a start of a date/time range
                                Can be of type String or datetime.
        @param  end_time:       (optional) Timestamp specifying the end of a date/time range
                                If not specified then we will query for validity on the start_time.
                                Can be of type String or datetime
        @throw  TypeError:  If input type is not as specified.
        @throw  ValueError:
        """
        if fill_id == "":
            raise TypeError("Fill_id should not be empty")

        # Converting all dates given as a String to a datetime object
        if validate_str(start_time):
            start_time = convert_date(start_time)
        elif validate_datetime(valid_until):
            # Strip off the microseconds
            start_time = start_time.replace(microsecond=0)
        if validate_str(end_time):
            end_time = convert_date(end_time)
        elif validate_datetime(end_time):
            # Strip off the microseconds
            end_time = end_time.replace(microsecond=0)

        if start_time > end_time:
            raise ValueError("Incorrect validity interval")

        fill = Fill()
        fill.fill_id = fill_id
        fill.start_time = start_time
        fill.end_time = end_time
        fill.save()

    def add_run(self, run_id, fill_id, start_time, end_time):
        """Add a new run to the database.

        @param  run_id:         String specifying the run number. Must
                                be unique. Must not contain a forward slash (i.e. /).
        @param  fill_id:        String specifying the fill number. Must exist in the database.
        @param  start_time:     (optional) Timestamp specifying a start of a date/time range
                                Can be of type String or datetime.
        @param  end_time:       (optional) Timestamp specifying the end of a date/time range
                                If not specified then we will query for validity on the start_date.
                                Can be of type String or datetime
        @throw  TypeError:  If input type is not as specified.
        @throw  ValueError:
        """
        if run_id == "" or fill_id == "":
            raise TypeError("Run_id or Fill_id should not be empty")

        # Converting all dates given as a String to a datetime object
        if validate_str(start_time):
            start_time = convert_date(start_time)
        elif validate_datetime(valid_until):
            # Strip off the microseconds
            start_time = start_time.replace(microsecond=0)
        if validate_str(end_time):
            end_time = convert_date(end_time)
        elif validate_datetime(end_time):
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

    def remove_run(self, run_id):
        """Remove a run from the database.

        @param  run_id:        String identifying the run to remove
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If run_id does not exist.
        """

    def list_runs(self, fill_id=None, start_time=None, end_time=None):
        """Return a list with runnumbers of all the runs in the database.

        @param fill_id:     (optional) String identifying the fill to which the runs belong
        @param  start_time:     Timestamp specifying a start of a date/time range
                                Can be of type String or datetime.
        @param  end_time:       (optional) Timestamp specifying the end of a date/time range
                                If not specified then we will query for validity on the start_date.
                                Can be of type String or datetime
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If fill_id does not exist.
        @retval List:           A list with (string) runs
        """

    def add_file(self, run_id, file_id, start_time, end_time):
        """Add a new file to the database.

        @param  file_id:        String specifying the file_id. Must
                                be unique. Must not contain a forward slash (i.e. /).
        @param run_id:          String identifying the run to which the files belong
        @param  start_time:     Timestamp specifying a start of a date/time range
                                Can be of type String or datetime.
        @param  end_time:       (optional) Timestamp specifying the end of a date/time range
                                If not specified then we will query for validity on the start_date.
                                Can be of type String or datetime
        @throw  TypeError:  If input type is not as specified.
        @throw  ValueError:
        """
        if run_id == "" or file_id == "":
            raise TypeError("Run_id or File_id should not be empty")

        # Converting all dates given as a String to a datetime object
        if validate_str(start_time):
            start_time = convert_date(start_time)
        elif validate_datetime(valid_until):
            # Strip off the microseconds
            start_time = start_time.replace(microsecond=0)
        if validate_str(end_time):
            end_time = convert_date(end_time)
        elif validate_datetime(end_time):
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

    def remove_file(self, file_id):
        """Remove a file from the database.

        @param  file_id:        String identifying the file to remove
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If file_id does not exist.
        """

    def list_files(self, fill_id=None, run_id=None, start_time=None, end_time=None):
        """Return a list with the paths of all the files in the database.

        @param fill_id:         (optional) String identifying the fill to which the files belong
        @param run_id:          (optional) String identifying the run to which the files belong
        @param  start_time:     Timestamp specifying a start of a date/time range
                                Can be of type String or datetime.
        @param  end_time:       (optional) Timestamp specifying the end of a date/time range
                                If not specified then we will query for validity on the start_date.
                                Can be of type String or datetime
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If fill_id or run_id does not exist.
        @retval List:           A list with (string) runs
        """

    def remove_fill(self, fill_id):
        """Remove a fill from the database.

        @param  fill_id:        String identifying the fill to remove
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If fill_id does not exist.
        """
        if not validate_str(fill_id):
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

    def add_detector(self, name, parent_id=None):
        """Add a new detector to the database.

        @param  name:       String specifying the name for the new detector. Must
                            be unique. Must not contain a forward slash (i.e. /).
        @param  parent_id:  (optional) String identifying the parent detector the
                            new detector should be added to as subdetector.
        @throw  TypeError:  If input type is not as specified.
        @throw  ValueError: If parent_id does not exist.
        """
        if not validate_str(name):
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
        name = sanitize_str(name)

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
                raise ValueError("The detector '" + name + "' already exists")

        # If we add a subdetector
        else:
            if not validate_path(parent_id):
                raise TypeError(
                    "Please pass the correct type of input: parent_id  "
                    "should be String"
                )

            parent_id = sanitize_path(parent_id)
            detector_names = split_detector_names(parent_id)

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
            except DoesNotExist:
                detector.subdetectors.append(added_detector)
                detector_wrapper.save()
                return
            raise ValueError("Detector '" + parent_id + "/" + name + "' already exist")

    def remove_detector(self, detector_id):
        """Remove a detector from the database.

        @param  detector_id:    String identifying the detector to remove (i.e.
                                'muonflux/driftTubes').
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If detector_id does not exist.
        """
        if not validate_str(detector_id):
            raise TypeError(
                "Please pass the correct type of input: detector_id should be String"
            )

        if detector_id == "":
            raise ValueError(
                "Please provide the correct input for detector_id: detector_id "
                "cannot be an empty String"
            )

        detector_id = sanitize_path(detector_id)

        try:
            wrapper = self.__get_wrapper(detector_id)
        except Exception as e:
            raise ValueError(
                "The detector '", detector_id, "' does not exist in the database"
            ) from e

        detector_names = split_detector_names(detector_id)
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

        for name in detector_names[:-1]:
            path += "/" + name

        path = sanitize_path(path)
        detector = self.__get_detector(wrapper, path)
        subdetectors = detector.subdetectors

        # Find the subdetector and remove it from the list
        for i, subdetector in enumerate(subdetectors):
            if subdetector.name == detector_names[-1]:
                detector.subdetectors.pop(i)
                break

        wrapper.save()

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
        """Add a condition to a detector.

        @param  detector_id:    String identifying the detector to which the
                                condition will be added (i.e. 'muonflux/driftTubes').
        @param  name:           String specifying the name of the condition (e.g. 'strawPositions').
        @param  tag:            String specifying a tag for the condition. Must be unique
                                for the same condition name.
        @param  values:         The values of the condition. Can be any data type.
        @param  type:           (optional) String specifying the type of condition (e.g. 'calibration').
        @param  collected_at:   (optional) Timestamp specifying the date/time the condition was
                                acquired. Must be unique w.r.t. the condition name.
                                Can be of type String or datetime. This timestamp will be stored
                                with an accuracy up to seconds.
                                If unspecified, this value will be set to 'datetime.now'.
        @param  valid_since:    (optional) Timestamp specifying the date/time as of when the
                                condition is valid. Can be of type String or datetime. This
                                timestamp will be stored with an accuracy up to seconds.
                                If unspecified, this value will be set to 'datetime.now'.
        @param valid_until:     (optional) Timestamp specifying the date/time up
                                until the condition is valid. Can be of type String or datetime.
                                If unspecified, this value will be set to 'datetime.max'. This
                                timestamp will be stored with an accuracy up to seconds.
        @throw TypeError:       If input type is not as specified.
        @throw ValueError:      If detector_id does not exist.
        """
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
            validate_path(detector_id) and validate_str(tag) and validate_str(name)
        ):
            raise TypeError(
                "Please pass the correct type of input: detector_id, "
                "tag, and name should be String"
            )

        if not (
            (validate_interval_parameters(valid_since) or valid_since is None)
            and (validate_interval_parameters(valid_until) or valid_until is None)
            and (validate_interval_parameters(collected_at) or collected_at is None)
        ):
            raise TypeError(
                "Please pass the correct type of input: valid_since, valid_until and collected_at "
                "should be either String or datetime object"
            )

        if not validate_str(condition_type) and condition_type is not None:
            raise TypeError(
                "Please pass the correct type of input: type should be String"
            )

        # Converting all dates given as a String to a datetime object
        if validate_str(valid_until):
            valid_until = convert_date(valid_until)
        elif validate_datetime(valid_until):
            # Strip off the microseconds
            valid_until = valid_until.replace(microsecond=0)
        if validate_str(valid_since):
            valid_since = convert_date(valid_since)
        elif validate_datetime(valid_since):
            # Strip off the microseconds
            valid_since = valid_since.replace(microsecond=0)
        if validate_str(collected_at):
            collected_at = convert_date(collected_at)
        elif validate_datetime(collected_at):
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

        name = sanitize_str(name)
        tag = sanitize_str(tag)

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

    def get_conditions(self, detector_id):
        """Return a list with all condition dictionaries associated with a detector.

        @param  detector_id:    String identifying the detector for which the
                                conditions must be retrieved (i.e. 'muonflux/driftTubes').
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If detector_id does not exist.
        @retval List:           A list with condition dictionaries adhering to the following
                                specification:
                                Condition = { 'name': String, 'tag': String, 'type': String,
                                              'collected_at': datetime, 'valid_since': datetime,
                                              'valid_until': datetime, 'values': mixed }
        """
        if not validate_str(detector_id):
            raise TypeError(
                "Please pass the correct type of input: detector_id should be String"
            )

        try:
            detector_wrapper = self.__get_wrapper(detector_id)
        except ValueError as e:
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

    def get_conditions_by_name(self, detector_id, name):
        """Return a list with condition dictionaries having a specific name for a given detector.

        @param  detector_id:    String identifying the detector for which the
                                conditions must be retrieved (i.e. 'muonflux/driftTubes').
        @param  name:           String specifying the name of the conditions to be retrieved (e.g.
                                'strawPositions').
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If detector_id does not exist.
        @retval List:           A list with condition dictionaries adhering to the following
                                specification:
                                Condition = { 'name': String, 'tag': String, 'type': String,
                                              'collected_at': datetime, 'valid_since': datetime,
                                              'valid_until': datetime, 'values': mixed }
        """
        # Input validation
        if not validate_str(detector_id):
            raise TypeError(
                "Please pass the correct type of input: detector_id should be String"
            )

        if not validate_str(name):
            raise TypeError(
                "Please pass the correct form of input: name should be String"
            )

        # Input sanitization
        name = sanitize_str(name)

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

    def get_conditions_by_tag(self, detector_id, tag):
        """Return a list with condition dictionaries having a specific tag for a given detector.

        @param  detector_id:    String identifying the detector for which the
                                condition must be retrieved (i.e. 'muonflux/driftTubes').
        @param  tag:            String specifying the tag of the condition to be retrieved.
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If detector_id does not exist.
        @retval List:           A list with condition dictionaries adhering to the following
                                specification:
                                Condition = { 'name': String, 'tag': String, 'type': String,
                                                'collected_at': datetime, 'valid_since': datetime,
                                                'valid_until': datetime, 'values': mixed }
        """
        # Input validation
        if not validate_str(detector_id):
            raise TypeError(
                "Please pass the correct type of input: detector_id should be String"
            )

        if not validate_str(tag):
            raise TypeError(
                "Please pass the correct format of input: tag should be String"
            )

        # Input sanitization
        tag = sanitize_str(tag)

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

    def get_conditions_by_name_and_validity(
        self, detector_id, name, start_date, end_date=None
    ):
        """Return a list of conditions dictionaries for a detector that are valid on the specified date.

        @param  detector_id:    String identifying the detector for which the
                                condition must be retrieved (i.e. 'muonflux/driftTubes').
        @param  name:           String specifying the name of the conditions to be retrieved (e.g.
                                'strawPositions').
        @param  start_date:     Timestamp specifying a start of a date/time range for which
                                conditions must be valid.
                                Can be of type String or datetime.
        @param  end_date:       (optional) Timestamp specifying the end of a date/time range for
                                which conditions must be valid.
                                If not specified then we will query for validity on the start_date.
                                Can be of type String or datetime
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If detector_id does not exist.
        @retval List:           A list with condition dictionaries adhering to the following
                                specification:
                                Condition = { 'name': String, 'tag': String, 'type': String,
                                                'collected_at': datetime, 'valid_since': datetime,
                                                'valid_until': datetime, 'values': mixed }
        """
        # Input validation
        if not validate_str(detector_id):
            raise TypeError(
                "Please pass the correct type of input: detector_id should be String"
            )

        if not (
            validate_str(name)
            and validate_interval_parameters(start_date)
            and (validate_interval_parameters(end_date) or end_date is None)
        ):
            raise TypeError(
                "Please pass the valid input type: name should be String, "
                "dates could be either datetime or String type."
            )

        # Input sanitization
        name = sanitize_str(name)

        # Converting all dates given as a String to a datetime object
        if validate_str(start_date):
            start_date = convert_date(start_date)
        elif validate_datetime(start_date):
            start_date = start_date.replace(microsecond=0)  # Strip off the microseconds
        if validate_str(end_date):
            end_date = convert_date(end_date)
        elif validate_datetime(end_date):
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

    def get_condition_by_name_and_tag(self, detector_id, name, tag):
        """Return a condition dictionary of a specific condition belonging to a detector, identified by condition name and tag. This combination must be unique.

        @param  detector_id:    String identifying the detector for which the
                                condition must be retrieved (i.e. 'muonflux/driftTubes').
        @param  name:           String specifying the name of the conditions to be retrieved (e.g.
                                'strawPositions').
        @param  tag:            String specifying the tag of the condition to be retrieved.
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If detector_id does not exist.
        @retval Dict:           A dictionary adhering to the following specification:
                                Condition = { 'name': String, 'tag': String, 'type': String,
                                                'collected_at': datetime, 'valid_since': datetime,
                                                'valid_until': datetime, 'values': mixed }
        """
        # Input validation
        if not validate_str(detector_id):
            raise TypeError(
                "Please pass the correct type of input: detector_id should be String"
            )

        if not (validate_str(name) and validate_str(tag)):
            raise TypeError(
                "Please pass the correct form of input: "
                "name and tag should be String"
            )

        # Input sanitization
        name = sanitize_str(name)
        tag = sanitize_str(tag)

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

    def get_condition_by_name_and_collection_date(
        self, detector_id, name, collected_at
    ):
        """Return a condition dictionary of a specific condition belonging to a detector, identified by condition name and collection date/time. This combination must be unique.

        @param  detector_id:    String identifying the detector for which the
                                condition must be retrieved (i.e. 'muonflux/driftTubes').
        @param  name:           String specifying the name of the conditions to be retrieved (e.g.
                                'strawPositions').
        @param  collected_at:   Timestamp specifying the moment on which the condition was
                                collected/measured. Can be of type String or datetime.
                                Collection dates are stored with accuracy up to seconds.

        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If detector_id does not exist.
        @retval Dict:           A dictionary adhering to the following specification:
                                Condition = { 'name': String, 'tag': String, 'type': String,
                                                'collected_at': datetime, 'valid_since': datetime,
                                                'valid_until': datetime, 'values': mixed }
        """
        # Input validation
        if not validate_str(detector_id):
            raise TypeError(
                "Please pass the correct type of input: detector_id should be String"
            )

        if not (validate_str(name) and validate_interval_parameters(collected_at)):
            raise TypeError(
                "Please pass the valid input type: name should be String, collected_at could be "
                "either datetime or String type."
            )

        # Input sanitization
        name = sanitize_str(name)

        # Converting all dates given as a String to a datetime object
        if validate_str(collected_at):
            collected_at = convert_date(collected_at)
        elif validate_datetime(collected_at):
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

    def update_condition_by_name_and_tag(
        self,
        detector_id,
        name,
        tag,
        condition_type=None,
        valid_since=None,
        valid_until=None,
    ):
        """Update the type, valid_since and valid_until values of a specific condition belonging to a detector, identified by condition name and tag.

        @param  detector_id:    String identifying the detector for which the
                                condition must be updated (i.e. 'muonflux/driftTubes').
        @param  name:           String specifying the name of the conditions to be updated (e.g.
                                'strawPositions').
        @param  tag:            String specifying the tag of the condition to be updated.
        @param  type:           (optional) String specifying the type of condition
                                (e.g. 'calibration').
        @param  valid_since:    (optional) Timestamp specifying the date/time as of when the
                                condition is valid. Can be of type String or datetime.
        @param  valid_until:    (optional) Timestamp specifying the date/time up until the
                                condition is valid. Can be of type String or datetime.
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If detector_id does not exist.
        """
        # Input validation
        if not validate_str(detector_id):
            raise TypeError(
                "Please pass the correct type of input: detector_id should be String"
            )

        if not (
            (validate_interval_parameters(valid_since) or valid_since is None)
            and (validate_interval_parameters(valid_until) or valid_until is None)
            and (validate_str(condition_type) or condition_type is None)
            and validate_str(name)
            and validate_str(tag)
        ):
            raise TypeError(
                "Please pass correct form of input: for valid_since and/or valid_until, "
                "they could be String, datetime or None. Only String is accepted for name, "
                "tag and type."
            )

        # Converting all dates given as a String to a datetime object
        if validate_str(valid_until):
            valid_until = convert_date(valid_until)
        elif validate_datetime(valid_until):
            # Strip off the microseconds
            valid_until = valid_until.replace(microsecond=0)
        if validate_str(valid_since):
            valid_since = convert_date(valid_since)
        elif validate_datetime(valid_since):
            # Strip off the microseconds
            valid_since = valid_since.replace(microsecond=0)

        if valid_until is not None and valid_since is not None:
            if valid_since > valid_until:
                raise ValueError("Invalid validity interval")

        # Input sanitization
        name = sanitize_str(name)
        tag = sanitize_str(tag)

        if validate_str(condition_type):
            condition_type = sanitize_str(condition_type)

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

    def add_attributes_to_brick(
        self,
        brick_id,
        emulsion_id=None,
        producer_id=None,
        batch_id=None,
        production_date=None,
        scanning_lab=None,
    ):
        """Add attributes to a brick.

        @param  emulsion_id:          String identifying the emulsion
        @param  brick_id:             String specifying the brick
        @param  producer_id:          String specifying the producer
        @param  batch_id:             String specifying the batch id
        @param  production_date:      Timestamp specifying production date and time
        @param  scanning_lab:         String specifying the scanning lab
        @throw TypeError:             If input type is not as specified.
        @throw ValueError:            If emulsion_id does not exist.
        """

    def add_attributes_to_emulsion(self, emulsion_id, target_configuration=None):
        """Add attributes to a emulsion.

        @param  emulsion_id:          String identifying the emulsion
        @param  target_configuration: String specifying the target configuration
        @throw TypeError:          If input type is not as specified.
        @throw ValueError:
        """

    def add_attributes_to_file(
        self, file_id, path=None, luminosity=None, nb_events=None, size=None, DQ=None
    ):
        """Add attributes to a file.

        @param  file_id:           String identifying the file
        @param  path:              String specifying the path
        @param  luminosity:        String specifying the integrated luminosity delivered by the LHC during the fill
        @param  nb_events:         String specifying the number of events
        @param  size:              String specifying the number of bytes of the file
        @param  DQ:                String specifying the data quality flag
        @throw TypeError:          If input type is not as specified.
        @throw ValueError:         If detector_id does not exist.
        """

    def add_attributes_to_fill(
        self,
        fill_id,
        luminosity=None,
        filling_scheme=None,
        energy=None,
        colliding_bunches=None,
        B1=None,
        B2=None,
    ):
        """Add attributes to a fill.

        @param  fill_id:           String identifying the fill
        @param  luminosity:        String specifying the integrated luminosity delivered by the LHC during the fill
        @param  filling_scheme:    String specifying the filling scheme, e.g. "single_10b_3_0_0_pilots_7nc_1c"
        @param  energy:            String specifying the energy e.g. "450GeV", "3.5TeV"
        @param  colliding_bunches: String specifying the number of colliding bunches at IP1
        @param  B1:                String specifying B1
        @param  B2:                String specifying B2
        @throw TypeError:          If input type is not as specified.
        @throw ValueError:         If detector_id does not exist.
        """

    def add_attributes_to_run(
        self,
        run_id,
        luminosity=None,
        nb_events=None,
        runtype=None,
        beam_status=None,
        status=None,
        HV=None,
        eor_status=None,
    ):
        """Add attributes to a run.

        @param  run_id:            String identifying the run
        @param  luminosity:        String specifying the integrated luminosity delivered by the LHC during the fill
        @param  nb_events:         String specifying the number of events
        @param  runtype:           String specifying the type of the run, e.g. 'Physics', Calibration', etc.
        @param  beam_status:       String specifying the status of the beam, e.g. 'stable beams'
        @param  status:            List of strings specifying excluded FE boards
        @param  HV:                List of strings specifying excluded HV channels
        @param  eor_status:        Strings specifying status at the end of the run, 'OK'
        @throw TypeError:          If input type is not as specified.
        @throw ValueError:         If detector_id does not exist.
        """

    def add_brick(self, brick_id, emulsion_id, start_time=None, end_time=None):
        """Add a new brick to the database.

        @param  brick_id:       String specifying the emulsion_id. Must
                                be unique. Must not contain a forward slash (i.e. /).
        @param  emulsion_id:    String specifying the emulsion_id. Must exist in the database.
        @param  start_time:     Timestamp specifying a start of a date/time range
                                Can be of type String or datetime.
        @param  end_time:       (optional) Timestamp specifying the end of a date/time range
                                If not specified then we will query for validity on the start_date.
                                Can be of type String or datetime
        @throw  TypeError:  If input type is not as specified.
        @throw  ValueError:
        """

    def remove_brick(self, brick_id):
        """Remove a brick from the database.

        @param  brick_id:    String identifying the emulsion to remove
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If emulsion_id does not exist.
        """

    def list_bricks(self, emulsion_id=None, start_time=None, end_time=None):
        """Return a list of all the bricks in the database emulsion.

        @param  start_time:     Timestamp specifying a start of a date/time range
                                Can be of type String or datetime.
        @param  end_time:       (optional) Timestamp specifying the end of a date/time range
                                If not specified then we will query for validity on the start_date.
                                Can be of type String or datetime
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:
        @retval List:           A list with (string) bricks
        """

    def add_emulsion(self, emulsion_id, start_time=None, end_time=None):
        """Add a new emulsion to the database.

        @param  emulsion_id:     String specifying the emulsion_id. Must
                            be unique. Must not contain a forward slash (i.e. /).
        @param  start_time:     Timestamp specifying a start of a date/time range
                                Can be of type String or datetime.
        @param  end_time:       (optional) Timestamp specifying the end of a date/time range
                                If not specified then we will query for validity on the start_time.
                                Can be of type String or datetime
        @throw  TypeError:  If input type is not as specified.
        @throw  ValueError:
        """

    def remove_emulsion(self, emulsion_id):
        """Remove an emulsion from the database.

        @param  emulsion_id:    String identifying the emulsion to remove
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If emulsion_id does not exist.
        """

    def list_emulsions(self, start_time=None, end_time=None):
        """Return a list of all the emulsions in the database.

        @param  start_time:     Timestamp specifying a start of a date/time range
                                Can be of type String or datetime.
        @param  end_time:       (optional) Timestamp specifying the end of a date/time range
                                If not specified then we will query for validity on the start_time.
                                Can be of type String or datetime
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:
        @retval List:           A list with (string) emulsions
        """

    def get_attributes(
        self, fill_id=None, run_id=None, file_id=None, emulsion_id=None, brick_id=None
    ):
        """Return a list with all attributes dictionaries associated with an object.

        @param  fill_id:        String identifying the fill
        @param  run_id:         String identifying the run
        @param  file_id:        String identifying the file
        @param  emulsion_id:    String identifying the emulsion
        @param  brick_id:       String identifying the brick
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If detector_id does not exist.
        @retval List:           A list with attributes dictionaries adhering to the following
                                specification:
                                Attributes = { 'name1': String , 'name2' : String, ...}
        """

    def update_attributes(
        self,
        fill_id=None,
        run_id=None,
        file_id=None,
        emulsion_id=None,
        brick_id=None,
        attributes=None,
    ):
        """Update the attributes of a specific item.

        @param  fill_id:        String identifying the fill
        @param  run_id:         String identifying the run
        @param  file_id:        String identifying the file
        @param  emulsion_id:    String identifying the emulsion
        @param  brick_id:       String identifying the brick
        @param  attributes      A list with attributes dictionaries adhering to the following
                                specification:
                                Attributes = { 'name1': String , 'name2' : String, ...}
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If detector_id does not exist.
        """

    def __del__(self):
        """Destruct by closing connection."""
        disconnect()
