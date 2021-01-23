from django.db import IntegrityError
from rest_framework import status
from rest_framework.views import Response, exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    if isinstance(exc, IntegrityError) and not response and "duplicate key value" in str(exc):
        response = Response(
            {"message": "Database error with duplicate key value, the uploaded data possibly already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return response
