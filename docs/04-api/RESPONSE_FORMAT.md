# API Response Format

Every endpoint must return a standardized response.

Success

{
  "success": true,
  "message": "Raffle created successfully.",
  "data": {}
}

Error

{
  "success": false,
  "message": "Validation failed.",
  "errors": [
    {
      "field": "title",
      "message": "Title is required."
    }
  ]
}

Pagination

{
  "success": true,
  "data": [],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 320,
    "total_pages": 16
  }
}