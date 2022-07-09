""" Contains a Mongo Engine model definition for a Brick. """
from mongoengine import EmbeddedDocument, EmbeddedDocumentListField, StringField, ComplexDateTimeField
#evh
from databases.mongodb.models.attribute import Attribute


## This model represents a brick. An brick is associated with zero
#  or more Attributes.
#
#  @property brick_id:        (string) brick number, must not be empty
#                             and must be unique.
#  @property emulsion_id      (string) Must not be empty and exist in the database.
#  @property attributes:      List of associated Attribute models.
#  @property start_time:      (datetime) The date/time defining the start of the brick configuration.
#  @property end_time:        (datetime) The date/time defining the end of the brick configuration.

class Brick(EmbeddedDocument):
    brick_id = StringField(max_length=1000, required=True)
    emulsion_id = StringField(max_length=1000, required=True)
    attributes = EmbeddedDocumentListField(Attribute)
    start_time = ComplexDateTimeField()
    end_time = ComplexDateTimeField()
