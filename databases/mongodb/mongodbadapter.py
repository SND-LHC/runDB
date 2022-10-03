"""This module implements a MongoDB storage back-end adapter."""
import atexit

from json import loads

## As of Python 3.8 we can do more with typing. It is recommended to make
## the adapter class final. Use the following import and provided
## decorator for the class.
from typing import final
from mongoengine import connect, DoesNotExist, disconnect


from databases.mongodb.models.fill import Fill
from databases.mongodb.models.run import Run
from databases.mongodb.models.file import File
from databases.mongodb.models.attribute import Attribute
from databases.mongodb.helpers import (
    sanitize_str,
    validate_datetime,
    validate_str,
    convert_date,
    create_uri,
)

# from databases.mongodb.models.target_configuration import TargetConfiguration

# from databases.mongodb.models.brick import Brick

from interface import APIInterface


# Package metadata
__authors__ = [
    "Nathan DPenha",
    "Juan van der Heijden",
    "Vladimir Romashov",
    "Raha Sadeghi",
    "Oliver Lantwin",
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

    def __get_fill(self, fill_id):
        """Get fill by id.

        @param  fill_id:         String identifying the fill to retrieve
        @retval Fill:            Fill object corresponding to query
        """
        return Fill.objects().get(fill_id=fill_id)

    def get_fill(self, fill_id):
        """Return a fill dictionary.

        @param  fill_id:        String identifying the fill to retrieve
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If fill_id does not exist.
        @retval Dict:           A dictionary adhering to the following specification:
                                Fill = { 'Fill_number': String,
                                         'Start_time': datetime,
                                         'End_time': datetime,
                                         'Attributes': Dict of Attributes }
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
        except ValueError as e:
            raise ValueError(
                "The requested fill " + fill_id + " does not exist."
            ) from e

        # Convert the internal Fill object to a generic Python dict type
        return loads(fill.to_json())

    def add_fill(self, fill_id, start_time, end_time, **attributes):
        """Add a new fill to the database.

        @param  fill_id:        String specifying the fill number. Must
                                be unique. Must not contain a forward slash (i.e. /). TODO make int?
        @param  start_time:     Timestamp specifying a start of a date/time range
                                Can be of type String or datetime.
        @param  end_time:       Timestamp specifying the end of a date/time range
                                Can be of type String or datetime
        @param  attributes:     Dict of attributes to be added to fill
        @throw  TypeError:  If input type is not as specified.
        @throw  ValueError:
        """
        if fill_id == "":
            # raise TypeError("fill_id should not be empty")
            print("WARNING: Fill ID empty.")
        try:
            self.__get_fill(fill_id)
            raise ValueError(f"Fill with {fill_id=} already exists. Abort.")
        except DoesNotExist:
            pass

        # Converting all dates given as a String to a datetime object
        if validate_str(start_time):
            start_time = convert_date(start_time)
        elif validate_datetime(start_time):
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

        if attributes:
            try:
                self.add_attributes_to_fill(fill_id, **attributes)
            except TypeError as e:
                raise TypeError(
                    "One of the passed attributes was not known."
                    "The fill was successfully added, but please check the attributes."
                ) from e

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
            # raise ValueError(
            #     "Please provide the correct input for fill_id: fill_id cannot be an empty String"
            # )
            print("WARNING: Fill ID empty.")

        try:
            fill = self.__get_fill(fill_id)
            fill.delete()
        except ValueError as e:
            raise ValueError(
                "The Fill '", fill_id, "' does not exist in the database"
            ) from e

    def list_fills(self, start_time=None, end_time=None):
        """Return a list with fill numbers of all fills in the database.

        Optionally filter fills to be within given time-range (or after start_time if only one given)

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
        fills = Fill.objects().all()
        if start_time:
            # Converting all dates given as a String to a datetime object
            if validate_str(start_time):
                start_time = convert_date(start_time)
            elif validate_datetime(start_time):
                # Strip off the microseconds
                start_time = start_time.replace(microsecond=0)
        if start_time and end_time:
            if validate_str(end_time):
                end_time = convert_date(end_time)
            elif validate_datetime(end_time):
                # Strip off the microseconds
                end_time = end_time.replace(microsecond=0)

            if start_time > end_time:
                raise ValueError("Incorrect validity interval")

        return [
            fill.fill_id
            for fill in fills
            if (not start_time or start_time <= fill.start_time)
            and (not (start_time and end_time) or (fill.end_time <= end_time))
        ]

    def __add_attributes_to_fill(self, fill_id, name, attribute_type, values):
        """Add general attribute to fill.

        @param fill_id:            String identifying the fill
        @param name:               Attribute name
        @param attribute_type:     Attribute type
        @param values:             Attribute value(s)
        @throw TypeError:          If input type is not as specified.
        @throw ValueError:         If fill_id does not exist.
        """
        fill = self.__get_fill(fill_id)
        try:
            fill.attributes.get(name=name)
            print(
                "WARNING: Attribute already exists, nothing done. Please update the attribute using TK"
            )
            # TODO add option to update?
            return
        except DoesNotExist:
            # Add a new attribute
            attribute = Attribute()
            attribute.name = name
            attribute.type = attribute_type
            attribute.values = values
            fill.attributes.append(attribute)
            fill.save()

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

        @param fill_id:           String identifying the fill
        @param luminosity:        String specifying the integrated luminosity delivered by the LHC during the fill
        @param filling_scheme:    String specifying the filling scheme, e.g. "single_10b_3_0_0_pilots_7nc_1c"
        @param energy:            String specifying the energy e.g. "450GeV", "3.5TeV"
        @param colliding_bunches: String specifying the number of colliding bunches at IP1
        @param B1:                String specifying B1
        @param B2:                String specifying B2
        @throw TypeError:          If input type is not as specified.
        @throw ValueError:         If detector_id does not exist.
        """
        # TODO Test how much speed is gained by doing all at once
        if not (
            luminosity or filling_scheme or energy or colliding_bunches or B1 or B2
        ):
            print("WARNING: no attribute specified. Nothing done.")
        if luminosity:
            # TODO validate luminosity?
            self.__add_attributes_to_fill(
                fill_id, name="luminosity", attribute_type="str", values=luminosity
            )
        if filling_scheme:
            self.__add_attributes_to_fill(
                fill_id,
                name="filling_scheme",
                attribute_type="str",
                values=filling_scheme,
            )
        if energy:
            # TODO validate energy?
            self.__add_attributes_to_fill(
                fill_id, name="energy", attribute_type="str", values=energy
            )
        if colliding_bunches:
            # TODO validate colliding bunches?
            self.__add_attributes_to_fill(
                fill_id,
                name="colliding_bunches",
                attribute_type="str",
                values=colliding_bunches,
            )
        if B1:
            # TODO validate B1? String or int?
            self.__add_attributes_to_fill(
                fill_id, name="B1", attribute_type="int", values=B1
            )
        if B2:
            # TODO validate B2?
            self.__add_attributes_to_fill(
                fill_id, name="B2", attribute_type="int", values=B2
            )

    def __get_run(self, run_id):
        """Get run by id.

        @param  run_id:         String identifying the run to retrieve
        @retval Run:            Run object corresponding to query
        """
        return Run.objects().get(run_id=run_id)

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
        except ValueError as e:
            raise ValueError("The requested run " + run_id + " does not exist.") from e

        # Convert the internal Run object to a generic Python dict type
        return loads(run.to_json())

    def add_run(self, run_id, fill_id, start_time, end_time, **attributes):
        """Add a new run to the database.

        @param  run_id:         String specifying the run number. Must
                                be unique. Must not contain a forward slash (i.e. /).
        @param  fill_id:        String specifying the fill number. Must exist in the database.
        @param  start_time:     Timestamp specifying a start of a date/time range
                                Can be of type String or datetime.
        @param  end_time:       Timestamp specifying the end of a date/time range
                                Can be of type String or datetime
        @param  attributes:     Dict of attributes to be added to fill
        @throw  TypeError:  If input type is not as specified.
        @throw  ValueError: If fill with fill_id does not exist
        """
        if run_id == "" or fill_id == "":
            # raise TypeError("run_id or fill_id should not be empty")
            print("run_id or fill_id should not be empty")
        try:
            self.__get_run(run_id)
            raise ValueError(f"Run with {run_id=} already exists. Abort.")
        except DoesNotExist:
            pass

        # Converting all dates given as a String to a datetime object
        if validate_str(start_time):
            start_time = convert_date(start_time)
        elif validate_datetime(start_time):
            # Strip off the microseconds
            start_time = start_time.replace(microsecond=0)
        if validate_str(end_time):
            end_time = convert_date(end_time)
        elif validate_datetime(end_time):
            # Strip off the microseconds
            end_time = end_time.replace(microsecond=0)

        if start_time > end_time:
            raise ValueError("Incorrect validity interval")

        try:
            fill = self.__get_fill(fill_id)
        except DoesNotExist as e:
            raise ValueError("Fill with fill_id " + fill_id + " does not exist.") from e

        if fill.start_time > start_time:
            raise ValueError("Start of run is before start of fill.")
        if fill.end_time < start_time:
            raise ValueError("Start of run is after end of fill.")
        if end_time > fill.end_time:
            raise ValueError("End of run is after end of fill.")

        run = Run()
        run.run_id = run_id
        run.fill_id = fill_id
        run.start_time = start_time
        run.end_time = end_time
        run.save()

        if attributes:
            try:
                self.add_attributes_to_run(run_id, **attributes)
            except TypeError as e:
                raise TypeError(
                    "One of the passed attributes was not known."
                    "The run was successfully added, but please check the attributes."
                ) from e

    def remove_run(self, run_id):
        """Remove a run from the database.

        @param  run_id:        String identifying the run to remove
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If run_id does not exist.
        """
        if not validate_str(run_id):
            raise TypeError(
                "Please pass the correct type of input: fill_id should be String"
            )

        if run_id == "":
            raise ValueError(
                "Please provide the correct input for fill_id: fill_id cannot be an empty String"
            )

        try:
            run = self.__get_run(run_id)
            run.delete()
        except ValueError as e:
            raise ValueError(
                "The run '", run_id, "' does not exist in the database"
            ) from e

    def list_runs(self, fill_id=None, start_time=None, end_time=None):
        """Return a list with runnumbers of all the runs in the database.

        Optionally, filter runs by fill_id or time window.

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
        runs = Run.objects().all()
        if start_time:
            # Converting all dates given as a String to a datetime object
            if validate_str(start_time):
                start_time = convert_date(start_time)
            elif validate_datetime(start_time):
                # Strip off the microseconds
                start_time = start_time.replace(microsecond=0)
        if start_time and end_time:
            if validate_str(end_time):
                end_time = convert_date(end_time)
            elif validate_datetime(end_time):
                # Strip off the microseconds
                end_time = end_time.replace(microsecond=0)

            if start_time > end_time:
                raise ValueError("Incorrect validity interval")

        return [
            run.run_id
            for run in runs
            if (not fill_id or run.fill_id == fill_id)
            and (not start_time or start_time <= run.start_time)
            and (not (start_time and end_time) or (run.end_time <= end_time))
        ]

    def __add_attributes_to_run(self, run_id, name, attribute_type, values):
        """Add general attribute to run.

        @param run_id:             String identifying the run
        @param name:               Attribute name
        @param attribute_type:     Attribute type
        @param values:             Attribute value(s)
        @throw TypeError:          If input type is not as specified.
        @throw ValueError:         If run_id does not exist.
        """
        run = self.__get_run(run_id)
        try:
            run.attributes.get(name=name)
            print(
                "WARNING: Attribute already exists, nothing done. Please update the attribute using TK"
            )
            # TODO add option to update?
            return
        except DoesNotExist:
            # Add a new attribute
            attribute = Attribute()
            attribute.name = name
            attribute.type = attribute_type
            attribute.values = values
            run.attributes.append(attribute)
            run.save()

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
        **additional_attributes,
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
        @param additional_attributes: dict of additonal attributes
        @throw TypeError:          If input type is not as specified.
        @throw ValueError:         If detector_id does not exist.
        """
        if not (
            luminosity
            or nb_events
            or runtype
            or beam_status
            or status
            or HV
            or eor_status
        ):
            print("WARNING: no attribute specified. Nothing done.")
        if luminosity:
            # TODO validate luminosity?
            self.__add_attributes_to_run(
                run_id, name="luminosity", attribute_type="str", values=luminosity
            )
        if nb_events:
            self.__add_attributes_to_run(
                run_id,
                name="number_of_events",
                attribute_type="int",  # String or Int?
                values=nb_events,
            )
        if runtype:
            self.__add_attributes_to_run(
                run_id, name="runtype", attribute_type="str", values=runtype
            )
        if beam_status:
            self.__add_attributes_to_run(
                run_id, name="beam_status", attribute_type="str", values=beam_status
            )
        if status:
            self.__add_attributes_to_run(
                run_id, name="status", attribute_type="str", values=status
            )
        if HV:
            self.__add_attributes_to_run(
                run_id, name="HV", attribute_type="str", values=HV
            )
        if eor_status:
            self.__add_attributes_to_run(
                run_id, name="eor_status", attribute_type="str", values=eor_status
            )
        for attribute, value in additional_attributes.items():
            self.__add_attributes_to_run(
                run_id, name=attribute, attribute_type="str", values=value
            )

    def __get_file(self, file_id):
        """Get file by id.

        @param  file_id:         String identifying the file to retrieve
        @retval File:            File object corresponding to query
        """
        return File.objects().get(file_id=file_id)

    def get_file(self, file_id):
        """Return a file dictionary.

        @param  file_id:        String identifying the file to retrieve
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If file_id does not exist.
        @retval Dict:           A dictionary adhering to the following specification:
                                File = { 'Path': String,
                                         'Start_time': datetime,
                                         'End_time': datetime,
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
        except ValueError as e:
            raise ValueError("The requested file" + file_id + " does not exist.") from e

        # Convert the internal File object to a generic Python dict type
        return loads(file.to_json())

    def add_file(self, run_id, file_id, start_time, end_time, **attributes):
        """Add a new file to the database.

        @param  file_id:        String specifying the file_id. Must
                                be unique. Must not contain a forward slash (i.e. /).
        @param  run_id:         String identifying the run to which the files belong
        @param  start_time:     Timestamp specifying a start of a date/time range
                                Can be of type String or datetime.
        @param  end_time:       Timestamp specifying the end of a date/time range
                                If not specified then we will query for validity on the start_date.
                                Can be of type String or datetime
        @param  attributes:     Dict of attributes to be added to file
        @throw  TypeError:  If input type is not as specified.
        @throw  ValueError:
        """
        if run_id == "" or file_id == "":
            raise TypeError("Run_id or File_id should not be empty")
        try:
            self.__get_file(file_id)
            raise ValueError(f"File with {file_id=} already exists. Abort.")
        except DoesNotExist:
            pass

        # Converting all dates given as a String to a datetime object
        if validate_str(start_time):
            start_time = convert_date(start_time)
        elif validate_datetime(start_time):
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

        try:
            run = self.__get_run(run_id)
        except DoesNotExist as e:
            raise ValueError("Run with run_id " + run_id + " does not exist.") from e

        if run.start_time > start_time:
            raise ValueError("Start of file is before start of run.")
        if run.end_time < start_time:
            raise ValueError("Start of file is after end of run.")
        if end_time > run.end_time:
            raise ValueError("End of file is after end of run.")

        file.run_id = run_id

        # if self.get_run(fill_id) == "":
        #     raise TypeError("Fill_id " + fill_id + " does not exist.")

        # file.fill_id = fill_id
        file.start_time = start_time
        file.end_time = end_time
        file.save()

        if attributes:
            try:
                self.add_attributes_to_file(file_id, **attributes)
            except TypeError as e:
                raise TypeError(
                    "One of the passed attributes was not known."
                    "The file was successfully added, but please check the attributes."
                ) from e

    def remove_file(self, file_id):
        """Remove a file from the database.

        @param  file_id:        String identifying the file to remove
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If file_id does not exist.
        """
        if not validate_str(file_id):
            raise TypeError(
                "Please pass the correct type of input: file_id should be String"
            )

        if file_id == "":
            raise ValueError(
                "Please provide the correct input for file_id: file_id cannot be an empty String"
            )

        try:
            f = self.__get_file(file_id)
            f.delete()
        except ValueError as e:
            raise ValueError(
                "The File '", file_id, "' does not exist in the database"
            ) from e

    def list_files(self, run_id=None, start_time=None, end_time=None):
        """Return a list with the paths of all the files in the database.

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
        files = File.objects().all()
        if start_time:
            # Converting all dates given as a String to a datetime object
            if validate_str(start_time):
                start_time = convert_date(start_time)
            elif validate_datetime(start_time):
                # Strip off the microseconds
                start_time = start_time.replace(microsecond=0)
        if start_time and end_time:
            if validate_str(end_time):
                end_time = convert_date(end_time)
            elif validate_datetime(end_time):
                # Strip off the microseconds
                end_time = end_time.replace(microsecond=0)

            if start_time > end_time:
                raise ValueError("Incorrect validity interval")

        # TODO feasible to filter by fill as well? probably better done by user
        return [
            f.file_id
            for f in files
            if (not run_id or f.run_id == run_id)
            and (not start_time or start_time <= f.start_time)
            and (not (start_time and end_time) or (f.end_time <= end_time))
        ]

    def __add_attributes_to_file(self, file_id, name, attribute_type, values):
        """Add general attribute to file.

        @param file_id:            String identifying the file
        @param name:               Attribute name
        @param attribute_type:     Attribute type
        @param values:             Attribute value(s)
        @throw TypeError:          If input type is not as specified.
        @throw ValueError:         If file_id does not exist.
        """
        f = self.__get_file(file_id)
        try:
            f.attributes.get(name=name)
            print(
                "WARNING: Attribute already exists, nothing done. Please update the attribute using TK"
            )
            # TODO add option to update?
            return
        except DoesNotExist:
            # Add a new attribute
            attribute = Attribute()
            attribute.name = name
            attribute.type = attribute_type
            attribute.values = values
            f.attributes.append(attribute)
            f.save()

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
        if not (path or luminosity or nb_events or size or DQ):
            print("WARNING: no attribute specified. Nothing done.")
        if luminosity:
            # TODO validate luminosity?
            self.__add_attributes_to_file(
                file_id, name="luminosity", attribute_type="str", values=luminosity
            )
        if nb_events:
            self.__add_attributes_to_file(
                file_id,
                name="number_of_events",
                attribute_type="int",  # String or Int?
                values=nb_events,
            )
        if size:
            self.__add_attributes_to_file(
                file_id, name="size", attribute_type="int", values=size
            )
        if DQ:
            self.__add_attributes_to_file(
                file_id, name="DQ", attribute_type="str", values=DQ
            )

    def get_target_configuration(self, target_configuration_id):
        """Return a target configuration dictionary.

        @param  target_configuration_id:    String identifying the target configuration to retrieve
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If target_configuration_id does not exist.
        @retval Dict:           A dictionary adhering to the following specification:
                                File = { 'TargetConfiguration_id': String, 'Start_time': datetime, 'End_time': datetime,
                                             'Attributes': List of Attributes }
        """
        if target_configuration_id == "":
            raise ValueError(
                "Please specify a valid target configuration ID. A target configuration ID cannot be empty."
            )

        if not validate_str(target_configuration_id):
            raise TypeError(
                "Please pass the correct type of input: target_configuration_id should be String"
            )

        target_configuration_id = sanitize_str(target_configuration_id)

        try:
            target_configuration = self.__get_file(target_configuration_id)
        except ValueError as e:
            raise ValueError(
                "The requested target_configuration "
                + target_configuration_id
                + " does not exist."
            ) from e

        # Convert the internal TargetConfiguration object to a generic Python dict type
        return loads(target_configuration.to_json())

    def add_target_configuration(
        self, target_configuration_id, start_time=None, end_time=None
    ):
        """Add a new target configuration to the database.

        @param  target_configuration_id:     String specifying the target_configuration_id. Must
                            be unique. Must not contain a forward slash (i.e. /).
        @param  start_time:     Timestamp specifying a start of a date/time range
                                Can be of type String or datetime.
        @param  end_time:       (optional) Timestamp specifying the end of a date/time range
                                If not specified then we will query for validity on the start_time.
                                Can be of type String or datetime
        @throw  TypeError:  If input type is not as specified.
        @throw  ValueError:
        """

    def remove_target_configuration(self, target_configuration_id):
        """Remove a target configuration from the database.

        @param  target_configuration_id:    String identifying the target_configuration to remove
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If target_configuration_id does not exist.
        """

    def list_target_configurations(self, start_time=None, end_time=None):
        """Return a list of all the target configurations in the database.

        @param  start_time:     Timestamp specifying a start of a date/time range
                                Can be of type String or datetime.
        @param  end_time:       (optional) Timestamp specifying the end of a date/time range
                                If not specified then we will query for validity on the start_time.
                                Can be of type String or datetime
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:
        @retval List:           A list with (string) target_configurations
        """

    def add_attributes_to_target_configuration(
        self, target_configuration_id, target_configuration=None
    ):
        """Add attributes to a target_configuration.

        @param  target_configuration_id:          String identifying the target_configuration
        @param  target_configuration: String specifying the target configuration
        @throw TypeError:          If input type is not as specified.
        @throw ValueError:
        """

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
        except ValueError as e:
            raise ValueError(
                "The requested brick" + brick_id + " does not exist."
            ) from e

        # Convert the internal Brick object to a generic Python dict type
        return loads(brick.to_json())

    def add_brick(
        self, brick_id, target_configuration_id, start_time=None, end_time=None
    ):
        """Add a new brick to the database.

        @param  brick_id:       String specifying the target_configuration_id. Must
                                be unique. Must not contain a forward slash (i.e. /).
        @param  target_configuration_id:    String specifying the target_configuration_id. Must exist in the database.
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

        @param  brick_id:    String identifying the target_configuration to remove
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If target_configuration_id does not exist.
        """

    def list_bricks(self, target_configuration_id=None, start_time=None, end_time=None):
        """Return a list of all the bricks in the database target_configuration.

        @param  start_time:     Timestamp specifying a start of a date/time range
                                Can be of type String or datetime.
        @param  end_time:       (optional) Timestamp specifying the end of a date/time range
                                If not specified then we will query for validity on the start_date.
                                Can be of type String or datetime
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:
        @retval List:           A list with (string) bricks
        """

    def add_attributes_to_brick(
        self,
        brick_id,
        producer_id=None,
        batch_id=None,
        production_date=None,
        scanning_lab=None,
    ):
        """Add attributes to a brick.

        @param  brick_id:             String specifying the brick
        @param  producer_id:          String specifying the producer
        @param  batch_id:             String specifying the batch id
        @param  production_date:      Timestamp specifying production date and time
        @param  scanning_lab:         String specifying the scanning lab
        @throw TypeError:             If input type is not as specified.
        @throw ValueError:            If target_configuration_id does not exist.
        """

    def get_attributes(
        self,
        fill_id=None,
        run_id=None,
        file_id=None,
        target_configuration_id=None,
        brick_id=None,
    ):
        """Return a list with all attributes dictionaries associated with an object.

        @param  fill_id:        String identifying the fill
        @param  run_id:         String identifying the run
        @param  file_id:        String identifying the file
        @param  target_configuration_id:    String identifying the target_configuration
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
        target_configuration_id=None,
        brick_id=None,
        attributes=None,
    ):
        """Update the attributes of a specific item.

        @param  fill_id:        String identifying the fill
        @param  run_id:         String identifying the run
        @param  file_id:        String identifying the file
        @param  target_configuration_id:    String identifying the target_configuration
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
