"""Conditions Database interface definition."""
from abc import ABCMeta, abstractmethod

## As of Python 3.8 we can do more with typing. It is recommended to make
## the API interface class final. Use the following import and provided
## decorator for the class.
from typing import final


# Package metadata
__author__ = "Tom Vrancken"
__email__ = "dev@tomvrancken.nl"
__copyright__ = "TU/e ST2019"
__credits__ = ["Juan van der Heijden", "Georgios Azis"]
__version__ = "1.0"
__status__ = "Prototype"


@final
class APIInterface(
    metaclass=ABCMeta
):  # For Python 3 we could/should use 'metaclass=ABCMeta'
    """
    Conditions Database Interface definition.

    This class defines the interface that all storage back-end adapters must implement.
    """

    @abstractmethod
    def list_fills(self, start_date=None, end_date=None):
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

    @abstractmethod
    def get_fill(self, fill_id):
        """Return a fill dictionary.

        @param  fill_id:        String identifying the fill to retrieve
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If fill_id does not exist.
        @retval Dict:           A dictionary adhering to the following specification:
                                Fill = { 'Fill_number': String, 'Start_time': datetime, 'End_time': datetime,
                                             'Attributes': List of Attributes }
        """

    @abstractmethod
    def add_fill(self, fill_id, start_time=None, end_time=None):
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

    @abstractmethod
    def remove_fill(self, fill_id):
        """Remove a fill from the database.

        @param  fill_id:        String identifying the fill to remove
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If fill_id does not exist.
        """

    @abstractmethod
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

    @abstractmethod
    def get_run(self, run_id):
        """Return a run dictionary.

        @param  run_id:         String identifying the run to retrieve
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If run_id does not exist.
        @retval Dict:           A dictionary adhering to the following specification:
                                Run = { 'Run_number': String, 'Start_time': datetime, 'End_time': datetime,
                                            'Attributes': List of Attributes }
        """

    @abstractmethod
    def add_run(self, run_id, fill_id, start_time=None, end_time=None):
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

    @abstractmethod
    def remove_run(self, run_id):
        """Remove a run from the database.

        @param  run_id:        String identifying the run to remove
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If run_id does not exist.
        """

    @abstractmethod
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

    @abstractmethod
    def get_file(self, file_id):
        """Return a file dictionary.

        @param  file_id:        String identifying the file to retrieve
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If file_id does not exist.
        @retval Dict:           A dictionary adhering to the following specification:
                                File = { 'Path': String, 'Start_time': datetime, 'End_time': datetime,
                                            'Attributes': List of Attributes }
        """

    @abstractmethod
    def add_file(self, file_id, run_id, start_time=None, end_time=None):
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

    @abstractmethod
    def remove_file(self, file_id):
        """Remove a file from the database.

        @param  file_id:        String identifying the file to remove
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If file_id does not exist.
        """

    @abstractmethod
    def list_target_configurations(self, start_time=None, end_time=None):
        """Return a list of all the target_configurations in the database.

        @param  start_time:     Timestamp specifying a start of a date/time range
                                Can be of type String or datetime.
        @param  end_time:       (optional) Timestamp specifying the end of a date/time range
                                If not specified then we will query for validity on the start_time.
                                Can be of type String or datetime
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:
        @retval List:           A list with (string) target_configurations
        """

    @abstractmethod
    def get_target_configuration(self, target_configuration_id):
        """Return an target_configuration dictionary.

        @param  target_configuration_id:    String identifying the target_configuration to retrieve
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If target_configuration_id does not exist.
        @retval Dict:           A dictionary adhering to the following specification:
                                File = { 'target_configuration_id': String, 'Start_time': datetime, 'End_time': datetime,
                                             'Attributes': List of Attributes }
        """

    @abstractmethod
    def add_target_configuration(
        self, target_configuration_id, start_time=None, end_time=None
    ):
        """Add a new target_configuration to the database.

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

    @abstractmethod
    def remove_target_configuration(self, target_configuration_id):
        """Remove an target_configuration from the database.

        @param  target_configuration_id:    String identifying the target_configuration to remove
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If target_configuration_id does not exist.
        """

    @abstractmethod
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

    @abstractmethod
    def get_brick(self, brick_id):
        """Return an brick dictionary.

        @param  brick_id:       String identifying the brick to retrieve
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If fill_id does not exist.
        @retval Dict:           A dictionary adhering to the following specification:
                                Brick = { 'Brick_id': String, 'Start_time': datetime, 'End_time': datetime,
                                             'Attributes': List of Attributes }
        """

    @abstractmethod
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

    @abstractmethod
    def remove_brick(self, brick_id):
        """Remove a brick from the database.

        @param  brick_id:    String identifying the target_configuration to remove
        @throw  TypeError:      If input type is not as specified.
        @throw  ValueError:     If target_configuration_id does not exist.
        """

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def add_attributes_to_target_configuration(
        self, target_configuration_id, target_configuration=None
    ):
        """Add attributes to a target_configuration.

        @param  target_configuration_id:          String identifying the target_configuration
        @param  target_configuration: String specifying the target configuration
        @throw TypeError:          If input type is not as specified.
        @throw ValueError:
        """

    @abstractmethod
    def add_attributes_to_brick(
        self,
        brick_id,
        target_configuration_id=None,
        producer_id=None,
        batch_id=None,
        production_date=None,
        scanning_lab=None,
    ):
        """Add attributes to a brick.

        @param  target_configuration_id:          String identifying the target_configuration
        @param  brick_id:             String specifying the brick
        @param  producer_id:          String specifying the producer
        @param  batch_id:             String specifying the batch id
        @param  production_date:      Timestamp specifying production date and time
        @param  scanning_lab:         String specifying the scanning lab
        @throw TypeError:             If input type is not as specified.
        @throw ValueError:            If target_configuration_id does not exist.
        """

    @abstractmethod
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

    @abstractmethod
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
