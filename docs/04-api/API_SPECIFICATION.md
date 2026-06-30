# API Specification

# Drawly REST API

Version: v1

Base URL

/api/v1

---

# Health

## Health Check

GET /health

Response

200 OK

{
  "success": true,
  "message": "API is running."
}

---

# Raffles

## Get All Raffles

GET /raffles

Query Params

page

page_size

search

status

sort

---

## Get Raffle

GET /raffles/{id}

---

## Create Raffle

POST /raffles

Request

{
  "title": "",
  "description": "",
  "prize": "",
  "ticket_price": 10000,
  "total_tickets": 100,
  "draw_date": "2026-08-01T19:00:00"
}

---

## Update Raffle

PUT /raffles/{id}

---

## Delete Raffle

DELETE /raffles/{id}

Soft Delete

---

## Publish Raffle

PATCH /raffles/{id}/publish

---

## Close Raffle

PATCH /raffles/{id}/close

---

## Select Winner

POST /raffles/{id}/winner

Response

{
    "ticket": 57,
    "participant": {},
    "winner_date": ""
}

---

# Public Raffles

## Get Public Raffle

GET /public/{slug}

---

## Get Available Tickets

GET /public/{slug}/tickets

---

## Reserve Tickets

POST /public/{slug}/reserve

Request

{
    "participant": {
        "full_name": "",
        "phone": "",
        "email": "",
        "address": "",
        "city": ""
    },
    "tickets": [
        1,
        2,
        3
    ]
}

---

# Participants

## List Participants

GET /participants

---

## Get Participant

GET /participants/{id}

---

## Update Participant

PUT /participants/{id}

---

## Delete Participant

DELETE /participants/{id}

---

# Tickets

## List Tickets

GET /tickets

---

## Ticket Detail

GET /tickets/{id}

---

## Update Ticket

PATCH /tickets/{id}

---

## Cancel Reservation

PATCH /tickets/{id}/cancel

---

# Dashboard

GET /dashboard

Returns

Active raffles

Revenue

Participants

Reserved Tickets

Available Tickets

Closed Raffles

---

# Future Endpoints

/users

/auth

/payments

/notifications

/reports

/settings

/webhooks

/organizations
