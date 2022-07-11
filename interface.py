""" Conditions Database interface definition. """
from abc import ABCMeta, abstractmethod
from datetime import datetime

## As of Python 3.8 we can do more with typing. It is recommended to make
## the API interface class final. Use the following import and provided
## decorator for the class.
# from typing import final


# Package metadata
__author__ = "Tom Vrancken"
__email__ = "dev@tomvrancken.nl"
__copyright__ = "TU/e ST2019"
__credits__ = ["Juan van der Heijden", "Georgios Azis"]
__version__ = "1.0"
__status__ = "Prototype"


_ABC = ABCMeta("ABC", (object,), {"__slots__": ()})  # Compatible with python 2 AND 3

### Conditions Database Interface definition. This class defines the interface that all
### storage back-end adapters must implement.
# TODO uncomment for python >= 3.8: @final
class APIInterface(_ABC):  # For Python 3 we could/should use 'metaclass=ABCMeta'

    ### Returns a list with fill numbers of all fills in the database.
    #   @param  start_date:     Timestamp specifying a start of a date/time range for which
    #                           conditions must be valid.
    #                           Can be of type String or datetime.
    #   @param  end_date:       (optional) Timestamp specifying the end of a date/time range for
    #                           which conditions must be valid.
    #                           If not specified then we will query for validity on the start_date.
    #                           Can be of type String or datetime
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:
    #   @retval List:           A list with (string) fill numbers
    @abstractmethod
    def list_fills(self, start_date=None, end_date=None):
        pass

    ### Returns a fill dictionary.
    #   @param  fill_id:        String identifying the fill to retrieve
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If fill_id does not exist.
    #   @retval Dict:           A dictionary adhering to the following specification:
    #                           Fill = { 'Fill_number': String, 'Start_time': datetime, 'End_time': datetime,
    #                                        'Attributes': List of Attributes }
    @abstractmethod
    def get_fill(self, fill_id):
        pass

    ### Adds a new fill to the database.
    #   @param  fill_id:        String specifying the fill number. Must
    #                           be unique. Must not contain a forward slash (i.e. /).
    #   @param  start_time:     Timestamp specifying a start of a date/time range
    #                           Can be of type String or datetime.
    #   @param  end_time:       (optional) Timestamp specifying the end of a date/time range
    #                           If not specified then we will query for validity on the start_time.
    #                           Can be of type String or datetime
    #   @throw  TypeError:  If input type is not as specified.
    #   @throw  ValueError:
    @abstractmethod
    def add_fill(self, fill_id, start_time=None, end_time=None):
        pass

    ### Removes a fill from the database. Caution:
    #   @param  fill_id:        String identifying the fill to remove
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If fill_id does not exist.
    @abstractmethod
    def remove_fill(self, fill_id):
        pass

    ### Returns a list with runnumbers of all the runs in the database.
    #   @param fill_id:     (optional) String identifying the fill to which the runs belong
    #   @param  start_time:     Timestamp specifying a start of a date/time range
    #                           Can be of type String or datetime.
    #   @param  end_time:       (optional) Timestamp specifying the end of a date/time range
    #                           If not specified then we will query for validity on the start_date.
    #                           Can be of type String or datetime
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If fill_id does not exist.
    #   @retval List:           A list with (string) runs
    # @abstractmethod
    # def list_runs(self, fill_id=None, start_time=None, end_time=None):
    #    pass

    ### Returns a run dictionary.
    #   @param  run_id:         String identifying the run to retrieve
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If run_id does not exist.
    #   @retval Dict:           A dictionary adhering to the following specification:
    #                           Run = { 'Run_number': String, 'Start_time': datetime, 'End_time': datetime,
    #                                        'Attributes': List of Attributes }
    # @abstractmethod
    # def get_run(self, run_id):
    #    pass

    ### Adds a new run to the database.
    #   @param  run_id:         String specifying the run number. Must
    #                           be unique. Must not contain a forward slash (i.e. /).
    #   @param  fill_id:        String specifying the fill number. Must exist in the database.
    #   @param  start_time:     (optional) Timestamp specifying a start of a date/time range
    #                           Can be of type String or datetime.
    #   @param  end_time:       (optional) Timestamp specifying the end of a date/time range
    #                           If not specified then we will query for validity on the start_date.
    #                           Can be of type String or datetime
    #   @throw  TypeError:  If input type is not as specified.
    #   @throw  ValueError:
    # @abstractmethod
    # def add_run(self, run_id, fill_id, start_time=None, end_time=None):
    #    pass

    ### Removes a run from the database. Caution:
    #   @param  run_id:        String identifying the run to remove
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If run_id does not exist.
    # @abstractmethod
    # def remove_run(self, run_id):
    #    pass

    ### Returns a list with the paths of all the files in the database.
    #   @param fill_id:         (optional) String identifying the fill to which the files belong
    #   @param run_id:          (optional) String identifying the run to which the files belong
    #   @param  start_time:     Timestamp specifying a start of a date/time range
    #                           Can be of type String or datetime.
    #   @param  end_time:       (optional) Timestamp specifying the end of a date/time range
    #                           If not specified then we will query for validity on the start_date.
    #                           Can be of type String or datetime
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If fill_id or run_id does not exist.
    #   @retval List:           A list with (string) runs
    # @abstractmethod
    # def list_files(self, fill_id=None, run_id=None, start_time=None, end_time=None):
    #    pass

    ### Returns a file dictionary.
    #   @param  file_id:        String identifying the file to retrieve
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If file_id does not exist.
    #   @retval Dict:           A dictionary adhering to the following specification:
    #                           File = { 'Path': String, 'Start_time': datetime, 'End_time': datetime,
    #                                        'Attributes': List of Attributes }
    # @abstractmethod
    # def get_file(self, file_id):
    #    pass

    ### Adds a new file to the database.
    #   @param  file_id:        String specifying the file_id. Must
    #                           be unique. Must not contain a forward slash (i.e. /).
    #   @param run_id:          String identifying the run to which the files belong
    #   @param  start_time:     Timestamp specifying a start of a date/time range
    #                           Can be of type String or datetime.
    #   @param  end_time:       (optional) Timestamp specifying the end of a date/time range
    #                           If not specified then we will query for validity on the start_date.
    #                           Can be of type String or datetime
    #   @throw  TypeError:  If input type is not as specified.
    #   @throw  ValueError:
    # @abstractmethod
    # def add_file(self, file_id, run_id, start_time=None, end_time=None):
    #    pass

    ### Removes a file from the database. Caution:
    #   @param  file_id:        String identifying the file to remove
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If file_id does not exist.
    # @abstractmethod
    # def remove_file(self, file_id):
    #    pass

    ### Returns a list of all the emulsions in the database.
    #   @param  start_time:     Timestamp specifying a start of a date/time range
    #                           Can be of type String or datetime.
    #   @param  end_time:       (optional) Timestamp specifying the end of a date/time range
    #                           If not specified then we will query for validity on the start_time.
    #                           Can be of type String or datetime
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:
    #   @retval List:           A list with (string) emulsions
    # @abstractmethod
    # def list_emulsions(self, start_time=None, end_time=None):
    #    pass

    ### Returns an emulsion dictionary.
    #   @param  emulsion_id:    String identifying the emulsion to retrieve
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If emulsion_id does not exist.
    #   @retval Dict:           A dictionary adhering to the following specification:
    #                           File = { 'Emulsion_id': String, 'Start_time': datetime, 'End_time': datetime,
    #                                        'Attributes': List of Attributes }
    # @abstractmethod
    # def get_emulsion(self, emulsion_id):
    #    pass

    ### Adds a new emulsion to the database.
    #   @param  emulsion_id:     String specifying the emulsion_id. Must
    #                       be unique. Must not contain a forward slash (i.e. /).
    #   @param  start_time:     Timestamp specifying a start of a date/time range
    #                           Can be of type String or datetime.
    #   @param  end_time:       (optional) Timestamp specifying the end of a date/time range
    #                           If not specified then we will query for validity on the start_time.
    #                           Can be of type String or datetime
    #   @throw  TypeError:  If input type is not as specified.
    #   @throw  ValueError:
    # @abstractmethod
    # def add_emulsion(self, emulsion_id, start_time=None, end_time=None):
    #    pass

    ### Removes an emulsion from the database. Caution:
    #   @param  emulsion_id:    String identifying the emulsion to remove
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If emulsion_id does not exist.
    # @abstractmethod
    # def remove_emulsion(self, emulsion_id):
    #    pass

    ### Returns a list of all the bricks in the database emulsion.
    #   @param  start_time:     Timestamp specifying a start of a date/time range
    #                           Can be of type String or datetime.
    #   @param  end_time:       (optional) Timestamp specifying the end of a date/time range
    #                           If not specified then we will query for validity on the start_date.
    #                           Can be of type String or datetime
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:
    #   @retval List:           A list with (string) bricks
    # @abstractmethod
    # def list_bricks(self, emulsion_id=None, start_time=None, end_time=None):
    #    pass

    ### Returns an brick dictionary.
    #   @param  brick_id:       String identifying the brick to retrieve
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If fill_id does not exist.
    #   @retval Dict:           A dictionary adhering to the following specification:
    #                           Brick = { 'Brick_id': String, 'Start_time': datetime, 'End_time': datetime,
    #                                        'Attributes': List of Attributes }
    # @abstractmethod
    # def get_brick(self, brick_id):
    #    pass

    ### Adds a new brick to the database.
    #   @param  brick_id:       String specifying the emulsion_id. Must
    #                           be unique. Must not contain a forward slash (i.e. /).
    #   @param  emulsion_id:    String specifying the emulsion_id. Must exist in the database.
    #   @param  start_time:     Timestamp specifying a start of a date/time range
    #                           Can be of type String or datetime.
    #   @param  end_time:       (optional) Timestamp specifying the end of a date/time range
    #                           If not specified then we will query for validity on the start_date.
    #                           Can be of type String or datetime
    #   @throw  TypeError:  If input type is not as specified.
    #   @throw  ValueError:
    # @abstractmethod
    # def add_brick(self, brick_id, emulsion_id, start_time=None, end_time=None):
    #    pass

    ### Removes a brick from the database. Caution:
    #   @param  brick_id:    String identifying the emulsion to remove
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If emulsion_id does not exist.
    # @abstractmethod
    # def remove_brick(self, brick_id):
    #    pass

    ### Adds attributes to a fill.
    #   @param  fill_id:           String identifying the fill
    #   @param  luminosity:        String specifying the integrated luminosity delivered by the LHC during the fill
    #   @param  filling_scheme:    String specifying the filling scheme, e.g. "single_10b_3_0_0_pilots_7nc_1c"
    #   @param  energy:            String specifying the energy e.g. "450GeV", "3.5TeV"
    #   @param  colliding_bunches: String specifying the number of colliding bunches at IP1
    #   @param  B1:                String specifying B1
    #   @param  B2:                String specifying B2
    #   @throw TypeError:          If input type is not as specified.
    #   @throw ValueError:         If detector_id does not exist.
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
        pass

    ### Adds attributes to a run.
    #   @param  run_id:            String identifying the run
    #   @param  luminosity:        String specifying the integrated luminosity delivered by the LHC during the fill
    #   @param  nb_events:         String specifying the number of events
    #   @param  runtype:           String specifying the type of the run, e.g. 'Physics', Calibration', etc.
    #   @param  beam_status:       String specifying the status of the beam, e.g. 'stable beams'
    #   @param  status:            List of strings specifying excluded FE boards
    #   @param  HV:                List of strings specifying excluded HV channels
    #   @param  eor_status:        Strings specifying status at the end of the run, 'OK'
    #   @throw TypeError:          If input type is not as specified.
    #   @throw ValueError:         If detector_id does not exist.
    # @abstractmethod
    # def add_attributes_to_run(self, run_id, luminosity=None, nb_events=None, runtype=None, beam_status=None,
    #                  status=None, HV=None, eor_status=None):
    #    pass

    ### Adds attributes to a file.
    #   @param  file_id:           String identifying the file
    #   @param  path:              String specifying the path
    #   @param  luminosity:        String specifying the integrated luminosity delivered by the LHC during the fill
    #   @param  nb_events:         String specifying the number of events
    #   @param  size:              String specifying the number of bytes of the file
    #   @param  DQ:                String specifying the data quality flag
    #   @throw TypeError:          If input type is not as specified.
    #   @throw ValueError:         If detector_id does not exist.
    # @abstractmethod
    # def add_attributes_to_run(self, file_id, path=None, luminosity=None, nb_events=None, size=None, DQ=None):
    #    pass

    ### Adds attributes to a emulsion.
    #   @param  emulsion_id:          String identifying the emulsion
    #   @param  target_configuration: String specifying the target configuration
    #   @throw TypeError:          If input type is not as specified.
    #   @throw ValueError:
    # @abstractmethod
    # def add_attributes_to_emulsion(self, emulsion_id, target_configuration=None):
    #    pass

    ### Adds attributes to a brick.
    #   @param  emulsion_id:          String identifying the emulsion
    #   @param  brick_id:             String specifying the brick
    #   @param  producer_id:          String specifying the producer
    #   @param  batch_id:             String specifying the batch id
    #   @param  production_date:      Timestamp specifying production date and time
    #   @param  scanning_lab:         String specifying the scanning lab
    #   @throw TypeError:             If input type is not as specified.
    #   @throw ValueError:            If emulsion_id does not exist.
    # @abstractmethod
    # def add_attributes_to_brick(self, brick_id, emulsion_id=None, producer_id=None, batch_id=None, production_date=None, scanning_lab=None):
    #    pass

    ### Returns a list with all attributes dictionaries associated with an object.
    #   @param  fill_id:        String identifying the fill
    #   @param  run_id:         String identifying the run
    #   @param  file_id:        String identifying the file
    #   @param  emulsion_id:    String identifying the emulsion
    #   @param  brick_id:       String identifying the brick
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If detector_id does not exist.
    #   @retval List:           A list with attributes dictionaries adhering to the following
    #                           specification:
    #                           Attributes = { 'name1': String , 'name2' : String, ...}
    # @abstractmethod
    # def get_attributes(self, fill_id=None, run_id=None, file_id=None, emulsion_id=None, brick_id=None):
    #    pass

    ### Updates the attributes of a specific item
    #   @param  fill_id:        String identifying the fill
    #   @param  run_id:         String identifying the run
    #   @param  file_id:        String identifying the file
    #   @param  emulsion_id:    String identifying the emulsion
    #   @param  brick_id:       String identifying the brick
    #   @param  attributes      A list with attributes dictionaries adhering to the following
    #                           specification:
    #                           Attributes = { 'name1': String , 'name2' : String, ...}
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If detector_id does not exist.
    # @abstractmethod
    # def update_attributes(self, fill_id=None, run_id=None, file_id=None, emulsion_id=None, brick_id=None, attributes=None)::
    #    pass

    ### Returns a list with all the detector names in the database.
    #   @param detector_id:     (optional) String identifying the parent detector to
    #                           retrieve the (sub)detector names for
    #                           (i.e. 'muonflux/driftTubes').
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If parent_id does not exist.
    #   @retval List:           A list with (string) names of detectors under the specified parent.
    @abstractmethod
    def list_detectors(self, parent_id=None):
        pass

    ### Returns a detector dictionary.
    #   @param  detector_id:    String identifying the detector to retrieve
    #                           (i.e. 'muonflux/driftTubes').
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If detector_id does not exist.
    #   @retval Dict:           A dictionary adhering to the following specification:
    #                           Detector = { 'name': String, 'subdetectors': List of Detector,
    #                                        'conditions': List of Condition }
    @abstractmethod
    def get_detector(self, detector_id):
        pass

    ### Adds a new detector to the database.
    #   @param  name:       String specifying the name for the new detector. Must
    #                       be unique. Must not contain a forward slash (i.e. /).
    #   @param  parent_id:  (optional) String identifying the parent detector the
    #                       new detector should be added to as subdetector.
    #   @throw  TypeError:  If input type is not as specified.
    #   @throw  ValueError: If parent_id does not exist.
    @abstractmethod
    def add_detector(self, name, parent_id=None):
        pass

    ### Removes a detector from the database. Caution: all conditions associated
    ### with this detector will be permanently removed as well!
    #   @param  detector_id:    String identifying the detector to remove (i.e.
    #                           'muonflux/driftTubes').
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If detector_id does not exist.
    @abstractmethod
    def remove_detector(self, detector_id):
        pass

    ### Adds a condition to a detector.
    #   @param  detector_id:    String identifying the detector to which the
    #                           condition will be added (i.e. 'muonflux/driftTubes').
    #   @param  name:           String specifying the name of the condition (e.g. 'strawPositions').
    #   @param  tag:            String specifying a tag for the condition. Must be unique
    #                           for the same condition name.
    #   @param  values:         The values of the condition. Can be any data type.
    #   @param  type:           (optional) String specifying the type of condition (e.g. 'calibration').
    #   @param  collected_at:   (optional) Timestamp specifying the date/time the condition was
    #                           acquired. Must be unique w.r.t. the condition name.
    #                           Can be of type String or datetime. This timestamp will be stored
    #                           with an accuracy up to seconds.
    #                           If unspecified, this value will be set to 'datetime.now'.
    #   @param  valid_since:    (optional) Timestamp specifying the date/time as of when the
    #                           condition is valid. Can be of type String or datetime. This
    #                           timestamp will be stored with an accuracy up to seconds.
    #                           If unspecified, this value will be set to 'datetime.now'.
    #   @param valid_until:     (optional) Timestamp specifying the date/time up
    #                           until the condition is valid. Can be of type String or datetime.
    #                           If unspecified, this value will be set to 'datetime.max'. This
    #                           timestamp will be stored with an accuracy up to seconds.
    #   @throw TypeError:       If input type is not as specified.
    #   @throw ValueError:      If detector_id does not exist.
    @abstractmethod
    def add_condition(
        self,
        detector_id,
        name,
        tag,
        values,
        type=None,
        collected_at=datetime.now(),
        valid_since=datetime.now(),
        valid_until=datetime.max,
    ):
        pass

    ### Returns a list with all condition dictionaries associated with a detector.
    #   @param  detector_id:    String identifying the detector for which the
    #                           conditions must be retrieved (i.e. 'muonflux/driftTubes').
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If detector_id does not exist.
    #   @retval List:           A list with condition dictionaries adhering to the following
    #                           specification:
    #                           Condition = { 'name': String, 'tag': String, 'type': String,
    #                                         'collected_at': datetime, 'valid_since': datetime,
    #                                         'valid_until': datetime, 'values': mixed }
    @abstractmethod
    def get_conditions(self, detector_id):
        pass

    ### Returns a list with condition dictionaries having a specific name for a given detector.
    #   @param  detector_id:    String identifying the detector for which the
    #                           conditions must be retrieved (i.e. 'muonflux/driftTubes').
    #   @param  name:           String specifying the name of the conditions to be retrieved (e.g.
    #                           'strawPositions').
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If detector_id does not exist.
    #   @retval List:           A list with condition dictionaries adhering to the following
    #                           specification:
    #                           Condition = { 'name': String, 'tag': String, 'type': String,
    #                                         'collected_at': datetime, 'valid_since': datetime,
    #                                         'valid_until': datetime, 'values': mixed }
    @abstractmethod
    def get_conditions_by_name(self, detector_id, name):
        pass

    ### Returns a list with condition dictionaries having a specific tag for a given detector.
    #   @param  detector_id:    String identifying the detector for which the
    #                           condition must be retrieved (i.e. 'muonflux/driftTubes').
    #   @param  tag:            String specifying the tag of the condition to be retrieved.
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If detector_id does not exist.
    #   @retval List:           A list with condition dictionaries adhering to the following
    #                           specification:
    #                           Condition = { 'name': String, 'tag': String, 'type': String,
    #                                         'collected_at': datetime, 'valid_since': datetime,
    #                                         'valid_until': datetime, 'values': mixed }
    @abstractmethod
    def get_conditions_by_tag(self, detector_id, tag):
        pass

    ### Returns a list with condition dictionaries associated with a detector that are valid on the
    ### specified date.
    #   @param  detector_id:    String identifying the detector for which the
    #                           condition must be retrieved (i.e. 'muonflux/driftTubes').
    #   @param  name:           String specifying the name of the conditions to be retrieved (e.g.
    #                           'strawPositions').
    #   @param  start_date:     Timestamp specifying a start of a date/time range for which
    #                           conditions must be valid.
    #                           Can be of type String or datetime.
    #   @param  end_date:       (optional) Timestamp specifying the end of a date/time range for
    #                           which conditions must be valid.
    #                           If not specified then we will query for validity on the start_date.
    #                           Can be of type String or datetime
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If detector_id does not exist.
    #   @retval List:           A list with condition dictionaries adhering to the following
    #                           specification:
    #                           Condition = { 'name': String, 'tag': String, 'type': String,
    #                                         'collected_at': datetime, 'valid_since': datetime,
    #                                         'valid_until': datetime, 'values': mixed }
    @abstractmethod
    def get_conditions_by_name_and_validity(
        self, detector_id, name, start_date, end_date=None
    ):
        pass

    ### Returns a condition dictionary of a specific condition belonging to a detector,
    ### identified by condition name and tag. This combination must be unique.
    #   @param  detector_id:    String identifying the detector for which the
    #                           condition must be retrieved (i.e. 'muonflux/driftTubes').
    #   @param  name:           String specifying the name of the conditions to be retrieved (e.g.
    #                           'strawPositions').
    #   @param  tag:            String specifying the tag of the condition to be retrieved.
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If detector_id does not exist.
    #   @retval Dict:           A dictionary adhering to the following specification:
    #                           Condition = { 'name': String, 'tag': String, 'type': String,
    #                                         'collected_at': datetime, 'valid_since': datetime,
    #                                         'valid_until': datetime, 'values': mixed }
    @abstractmethod
    def get_condition_by_name_and_tag(self, detector_id, name, tag):
        pass

    ### Returns a condition dictionary of a specific condition belonging to a detector, identified
    ### by condition name and collection date/time. This combination must be unique.
    #   @param  detector_id:    String identifying the detector for which the
    #                           condition must be retrieved (i.e. 'muonflux/driftTubes').
    #   @param  name:           String specifying the name of the conditions to be retrieved (e.g.
    #                           'strawPositions').
    #   @param  collected_at:   Timestamp specifying the moment on which the condition was
    #                           collected/measured. Can be of type String or datetime.
    #                           Collection dates are stored with accuracy up to seconds.
    #
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If detector_id does not exist.
    #   @retval Dict:           A dictionary adhering to the following specification:
    #                           Condition = { 'name': String, 'tag': String, 'type': String,
    #                                         'collected_at': datetime, 'valid_since': datetime,
    #                                         'valid_until': datetime, 'values': mixed }
    @abstractmethod
    def get_condition_by_name_and_collection_date(
        self, detector_id, name, collected_at
    ):
        pass

    ### Updates the type, valid_since and valid_until values of a specific condition
    ### belonging to a detector, identified by condition name and tag.
    #   @param  detector_id:    String identifying the detector for which the
    #                           condition must be updated (i.e. 'muonflux/driftTubes').
    #   @param  name:           String specifying the name of the conditions to be updated (e.g.
    #                           'strawPositions').
    #   @param  tag:            String specifying the tag of the condition to be updated.
    #   @param  type:           (optional) String specifying the type of condition
    #                           (e.g. 'calibration').
    #   @param  valid_since:    (optional) Timestamp specifying the date/time as of when the
    #                           condition is valid. Can be of type String or datetime.
    #   @param  valid_until:    (optional) Timestamp specifying the date/time up until the
    #                           condition is valid. Can be of type String or datetime.
    #   @throw  TypeError:      If input type is not as specified.
    #   @throw  ValueError:     If detector_id does not exist.
    @abstractmethod
    def update_condition_by_name_and_tag(
        self, detector_id, name, tag, type=None, valid_since=None, valid_until=None
    ):
        pass
