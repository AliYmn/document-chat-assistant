# Document Chat Assistant - Error Codes Reference

This document contains the error codes and descriptions used in the Document Chat Assistant application. Error codes are used to ensure consistent error handling across different components of the application.

## Error Code Structure

Error codes are organized according to the following structure:

- **1000-1999**: General errors
- **2000-2999**: Server errors
- **3000-3999**: Authentication and user errors

Each error code includes the following information:
- **Code**: Unique numerical error code
- **Message**: Brief description of the error
- **HTTP Status Code**: Corresponding HTTP status code

## General Errors (1000-1999)

| Code | Message                 | HTTP Status Code | Description                                                |
|------|-------------------------|-----------------|------------------------------------------------------------|
| 1000 | UNKNOWN_ERROR           | 500             | An undefined error occurred                                |
| 1001 | VALIDATION_FAILED       | 400             | The submitted data failed validation checks                |
| 1002 | UNAUTHORIZED_ACCESS     | 401             | Authentication is required                                 |
| 1003 | FORBIDDEN               | 403             | No permission to access                                    |
| 1004 | RESOURCE_NOT_FOUND      | 404             | The requested resource was not found                        |
| 1005 | METHOD_NOT_ALLOWED      | 405             | HTTP method is not supported for this endpoint             |
| 1006 | CONFLICT                | 409             | The request conflicts with the current state of the server |
| 1007 | UNSUPPORTED_MEDIA_TYPE  | 415             | Request content is in an unsupported format                |
| 1008 | RATE_LIMIT_EXCEEDED     | 429             | Too many requests sent, please try again later             |
| 1009 | PAYLOAD_TOO_LARGE       | 413             | Request size is too large                                  |
| 1010 | INVALID_FILE_TYPE       | 400             | Unsupported file type                                      |

## Server Errors (2000-2999)

| Code | Message                   | HTTP Status Code | Description                                                 |
|------|---------------------------|-----------------|-------------------------------------------------------------|
| 2000 | INTERNAL_SERVER_ERROR     | 500             | An error occurred within the server                          |
| 2001 | SERVICE_UNAVAILABLE       | 503             | Service is temporarily unavailable                           |
| 2002 | REQUEST_TIMEOUT           | 504             | Request timed out                                            |
| 2003 | BAD_GATEWAY               | 502             | Server received an invalid response while acting as a gateway|
| 2004 | BAD_REQUEST               | 400             | Invalid request format                                       |

## Authentication and User Errors (3000-3999)

| Code | Message                               | HTTP Status Code | Description                                                 |
|------|---------------------------------------|-----------------|-------------------------------------------------------------|
| 3000 | DUPLICATE_ENTRY                       | 400             | The same record already exists                              |
| 3001 | DEPENDENCY_FAILURE                    | 424             | A dependent service or component failed                     |
| 3002 | AUTHENTICATION_FAILED                 | 401             | Authentication failed                                       |
| 3003 | INVALID_TOKEN                         | 401             | Invalid authentication token                                |
| 3004 | EXPIRED_TOKEN                         | 401             | Authentication token has expired                            |
| 3005 | WEAK_PASSWORD                         | 400             | Password does not meet security requirements                |
| 3006 | INVALID_EMAIL                         | 400             | Invalid email format                                        |
| 3007 | INVALID_PHONE_NUMBER                  | 400             | Invalid phone number format                                 |
| 3008 | INVALID_USERNAME                      | 400             | Invalid username format                                     |
| 3009 | USERNAME_TAKEN                        | 409             | Username is already taken                                   |
| 3010 | EMAIL_TAKEN                           | 409             | Email address is already registered                         |
| 3011 | INVALID_CREDENTIALS                   | 401             | Invalid username or password                                |
| 3012 | INACTIVE_USER                         | 403             | User account is not active                                  |
| 3013 | USER_NOT_FOUND                        | 404             | User not found                                              |
| 3014 | INVALID_RESET_TOKEN                   | 400             | Invalid or expired password reset token                     |
| 3015 | USER_ALREADY_EXISTS                   | 409             | User already exists                                         |
| 3016 | INVALID_PARAMETERS                    | 400             | Invalid parameters                                          |

## Error Response Format

Error responses from the API will be in the following JSON format:

```json
{
  "error_code": 1001,
  "error_message": "VALIDATION_FAILED",
  "status_code": 400
}
```

## Catching and Handling Errors

The `ExceptionBase` class is used to catch and handle errors in the application:

```python
from libs.exceptions import ExceptionBase, ErrorCode

# Example of throwing an error
raise ExceptionBase(ErrorCode.USER_NOT_FOUND)
```

Example of error handling in FastAPI endpoints:

```python
from fastapi import Depends, HTTPException
from libs.exceptions import ExceptionBase, ErrorCode

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await find_user(user_id)
    if not user:
        raise ExceptionBase(ErrorCode.USER_NOT_FOUND)
    return user
```

## Adding Custom Error Codes

To add new error codes, you can add new values to the `ErrorCode` enum class in the `libs/exceptions/errors.py` file.
