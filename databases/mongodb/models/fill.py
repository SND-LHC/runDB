""" Contains a Mongo Engine model definition for a Fill. """
from mongoengine import (
    EmbeddedDocument,
    EmbeddedDocumentListField,
    StringField,
    ComplexDateTimeField,
)

# evh
from databases.mongodb.models.attribute import Attribute


## This model represents a fill. A fill is associated with zero
#  or more Attributes.
#
#  @property fill_id:         (string) Fill number, must not be empty
#                             and must be unique.
#  @property attributes:      List of associated Attribute models.
#  @property start_time:      (datetime) The date/time defining the start of the fill.
#  @property end_time:        (datetime) The date/time defining the end of the fill.


class Fill(EmbeddedDocument):
    fill_id = StringField(max_length=1000, required=True)
    attributes = EmbeddedDocumentListField(Attribute)
    start_time = ComplexDateTimeField()
    end_time = ComplexDateTimeField()
