""" Contains a Mongo Engine model definition for an Attribute. """
from mongoengine import EmbeddedDocument, DynamicField, StringField, ComplexDateTimeField


## This model describes a specific (set of) attributes with 
#  value(s) associated with a Fill, Run, File,Emulsion or Brick.
#  @property name:            (string) Name of the attribute; must not be empty.
#  @property type:            (string) Type of the attribute.
#  @property values:          (mixed) Values for / describing the attribute.
class Condition(EmbeddedDocument):
    name = StringField(max_length=1000, required=True)
    type = StringField(max_length=1000)
    values = DynamicField()
