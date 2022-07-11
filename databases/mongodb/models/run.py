""" Contains a Mongo Engine model definition for a Run. """
from mongoengine import (
    EmbeddedDocument,
    EmbeddedDocumentListField,
    StringField,
    ComplexDateTimeField,
)

# evh
from databases.mongodb.models.attribute import Attribute


## This model represents a run. A run is associated with zero
#  or more Attributes.
#
#  @property run_id:          (string) Run number, must not be empty
#                             and must be unique.
#  @property fill_id:         (string) Fill number, must not be empty and exist.
#  @property attributes:      List of associated Attribute models.
#  @property start_time:      (datetime) The date/time defining the start of the run.
#  @property end_time:        (datetime) The date/time defining the end of the run.


class Run(EmbeddedDocument):
    run_id = StringField(max_length=1000, required=True)
    fill_id = StringField(max_length=1000, required=True)
    attributes = EmbeddedDocumentListField(Attribute)
    start_time = ComplexDateTimeField()
    end_time = ComplexDateTimeField()
