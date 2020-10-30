from django.db.models import FileField

class VariableStorageFileField(FileField):
    """
    Disregard the storage kwarg when creating migrations for this field, so as to make migrations
    not vary based on environment variables.
    https://stackoverflow.com/questions/32349635/django-migrations-and-filesystemstorage-depending-on-settings
    """

    def deconstruct(self):
        name, path, args, kwargs = super(VariableStorageFileField, self).deconstruct()
        kwargs.pop('storage', None)
        return name, path, args, kwargs
