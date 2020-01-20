import logging

import magic
from django.core.exceptions import ValidationError

from django.utils.deconstruct import deconstructible
from django.template.defaultfilters import filesizeformat

logger = logging.getLogger(__name__)


@deconstructible
class FileValidator(object):
    error_messages = {
        "max_size": ("Ensure this file size is not greater than %(max_size)s." " Your file size is %(size)s."),
        "min_size": ("Ensure this file size is not less than %(min_size)s. " "Your file size is %(size)s."),
        "content_type": "Files of type %(content_type)s are not supported.",
        "magic_type": "Files of magic type %(magic_type)s are not supported.",
    }

    def __init__(self, max_size=None, min_size=None, content_types=(), magic_types=()):
        self.max_size = max_size
        self.min_size = min_size
        self.content_types = content_types
        self.magic_types = magic_types

    def __call__(self, data):
        if self.max_size is not None and data.size > self.max_size:
            params = {
                "max_size": filesizeformat(self.max_size),
                "size": filesizeformat(data.size),
            }
            raise ValidationError(self.error_messages["max_size"], "max_size", params)

        if self.min_size is not None and data.size < self.min_size:
            params = {"min_size": filesizeformat(self.mix_size), "size": filesizeformat(data.size)}
            raise ValidationError(self.error_messages["min_size"], "min_size", params)

        if self.content_types:
            content_type = magic.from_buffer(data.read(), mime=True)
            data.seek(0)

            if content_type not in self.content_types:
                params = {"content_type": content_type}
                raise ValidationError(self.error_messages["content_type"], "content_type", params)

        if self.magic_types:
            magic_type = magic.from_buffer(data.read())
            data.seek(0)

            if not any(ref_magic_type in magic_type for ref_magic_type in self.magic_types):
                params = {"magic_type": magic_type}
                raise ValidationError(self.error_messages["magic_type"], "magic_type", params)

    def __eq__(self, other):
        return (
            isinstance(other, FileValidator)
            and self.max_size == other.max_size
            and self.min_size == other.min_size
            and self.content_types == other.content_types
        )
