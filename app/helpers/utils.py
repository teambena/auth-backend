from wtforms.validators import StopValidation
from wtforms.validators import ValidationError
class OptionalButNotEmpty(object):
    """
    Allows missing but not empty input and stops the validation chain from continuing.
    """
    field_flags = ('optional', )

    def __call__(self, form, field):
        if not field.raw_data:
            raise StopValidation()
