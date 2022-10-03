"""Mongo Engine model definition for a target configuration."""
from mongoengine import (
    Document,
    EmbeddedDocumentListField,
    StringField,
    ComplexDateTimeField,
)

from databases.mongodb.models.attribute import Attribute


class TargetConfiguration(Document):
    """This model represents a target configuration.

    A target configuration is associated with zero or more Attributes.

     @property target_configuration_id:     (string) Target configuration ID, must not be empty
                                and must be unique.
     @property attributes:      List of associated Attribute models.
     @property start_time:      (datetime) The date/time defining the start of the target configuration.
     @property end_time:        (datetime) The date/time defining the end of the target configuration.
    """

    target_configuration_id = StringField(max_length=1000, required=True)
    attributes = EmbeddedDocumentListField(Attribute)
    start_time = ComplexDateTimeField()
    end_time = ComplexDateTimeField()
