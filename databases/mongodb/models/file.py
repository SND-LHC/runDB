"""Mongo Engine model definition for a File."""
from mongoengine import (
    Document,
    EmbeddedDocumentListField,
    StringField,
    ComplexDateTimeField,
)

from databases.mongodb.models.attribute import Attribute


class File(Document):
    """This model represents a file. A file is associated with zero or more Attributes.

    @property file_id:         (string) Filenumber, must not be empty
                            and must be unique.
    @property run_id:          (string) Runnumber, must exist in the database
    @property attributes:      List of associated Attribute models.
    @property start_time:      (datetime) The date/time defining the start of the file.
    @property end_time:        (datetime) The date/time defining the end of the file.
    """

    file_id = StringField(max_length=1000, required=True)
    run_id = StringField(max_length=1000, required=True)
    attributes = EmbeddedDocumentListField(Attribute)
    start_time = ComplexDateTimeField()
    end_time = ComplexDateTimeField()
