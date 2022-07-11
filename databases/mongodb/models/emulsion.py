""" Contains a Mongo Engine model definition for an Emulsion. """
from mongoengine import (
    EmbeddedDocument,
    EmbeddedDocumentListField,
    StringField,
    ComplexDateTimeField,
)

# evh
from databases.mongodb.models.attribute import Attribute


## This model represents an emulsion (target) configuration. An emulsion is associated with zero
#  or more Attributes.
#
#  @property emulsion_id:     (string) Emulsion number, must not be empty
#                             and must be unique.
#  @property attributes:      List of associated Attribute models.
#  @property start_time:      (datetime) The date/time defining the start of the emulsion configuration.
#  @property end_time:        (datetime) The date/time defining the end of the emulsion configuration.


class Emulsion(EmbeddedDocument):
    emulsion_id = StringField(max_length=1000, required=True)
    attributes = EmbeddedDocumentListField(Attribute)
    start_time = ComplexDateTimeField()
    end_time = ComplexDateTimeField()
