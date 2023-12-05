from functools import wraps
from flask import request, abort
from jsonschema import validate, ValidationError

def validate_request(validation_schema):
    def validation_decorator(wrapped_func):
        @wraps(wrapped_func)
        def decorated_validation_function(*args, **kwargs):
            try:
                validate(
                    instance=request.get_json(),
                    schema=validation_schema,
                )
            except ValidationError as e:
                abort(400, e.message)

            return wrapped_func(*args, **kwargs)
        return decorated_validation_function
    return validation_decorator
