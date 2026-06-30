# System Architecture

# Drawly

> Modern Raffle Management Platform

---

# Purpose

This document defines the architectural principles, system organization, module boundaries, and design decisions that will guide the development of Drawly.

The architecture has been designed to support long-term scalability while maintaining simplicity during the MVP stage.

The initial implementation will be a **Modular Monolith**, allowing the system to evolve into microservices if future business requirements demand it.

---

# Architectural Principles

Every component of Drawly must follow these principles.

## Scalability

The architecture should support future growth without requiring major refactoring.

---

## Modularity

Business domains should remain isolated.

Each module owns its own responsibilities.

---

## Low Coupling

Modules should know as little as possible about each other.

Communication should happen through clearly defined interfaces.

---

## High Cohesion

Classes, services, and modules should have one clear responsibility.

---

## Separation of Concerns

Business logic must never live inside controllers or UI components.

---

## Clean Code

Readable code is more valuable than clever code.

---

## SOLID

All modules should respect SOLID principles whenever applicable.

---

## Domain-Oriented Design

The architecture is organized around business domains rather than technical layers.

---

# Architectural Style

Drawly follows a **Modular Monolith Architecture**.

```

                Drawly

          ┌──────────────────┐
          │     Frontend     │
          └────────┬─────────┘
                   │
             REST API
                   │
          ┌────────▼─────────┐
          │     FastAPI      │
          └────────┬─────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
Raffles       Participants     Dashboard
    │              │              │
    └──────────────┼──────────────┘
                   │
             SQLModel ORM
                   │
             PostgreSQL

```

---

# Why Modular Monolith?

Advantages

- Easier deployment
- Lower infrastructure cost
- Simpler development
- Easier debugging
- Excellent performance
- Easy migration to microservices

At the current stage, microservices would introduce unnecessary complexity.

---

# System Layers

```

Presentation

↓

Application

↓

Domain

↓

Infrastructure

↓

Database

```

---

## Presentation Layer

Responsibilities

- HTTP Controllers
- Request Validation
- Response Formatting
- Authentication (future)

Contains no business logic.

---

## Application Layer

Coordinates business use cases.

Examples

Create Raffle

Reserve Ticket

Close Raffle

Select Winner

---

## Domain Layer

Contains all business rules.

Example

A ticket cannot be assigned twice.

Only active raffles accept participants.

Winning ticket must belong to an existing participant.

---

## Infrastructure Layer

Responsible for

Database

Repositories

External APIs

File Storage

Logging

Emails (future)

Payments (future)

---

# Module Organization

Each business capability becomes an independent module.

```

app/

modules/

auth/

raffles/

tickets/

participants/

dashboard/

payments/

notifications/

files/

shared/

```

Each module owns:

Controllers

Services

Schemas

Repositories

Domain Logic

Models

Exceptions

Tests

---

# Dependency Rules

Modules may depend on

Shared

Core

Infrastructure

They should NOT directly depend on other modules.

Instead they communicate through services.

---

# Frontend Architecture

Frontend follows Feature-Based Organization.

```

apps/web/

features/

raffles/

participants/

dashboard/

shared/

components/

hooks/

services/

types/

utils/

```

Each feature contains everything related to that domain.

---

# State Management

Client State

Zustand

Server State

TanStack Query

Form State

React Hook Form

Validation

Zod

---

# Backend Architecture

FastAPI is organized by domains.

```

app/

api/

core/

database/

models/

repositories/

schemas/

services/

modules/

middleware/

utils/

```

Business logic always lives inside services.

Repositories only access data.

---

# Data Flow

```

Browser

↓

React

↓

TanStack Query

↓

FastAPI

↓

Service

↓

Repository

↓

PostgreSQL

```

---

# Error Handling

Every request should return standardized responses.

```

Success

{
"success": true,
"data": {}
}

```

```

Error

{
"success": false,
"message": "",
"errors": []
}

```

---

# Validation Strategy

Frontend

Zod

↓

Backend

Pydantic

↓

Database

Constraints

Validation must exist at every layer.

---

# Logging

Application logs

Business logs

Audit logs

Future

Centralized logging.

---

# Security

Future modules include

JWT Authentication

Refresh Tokens

Rate Limiting

CSRF Protection

Input Sanitization

Password Hashing

Audit Logs

HTTPS

---

# File Storage

Current

Local Storage

Future

Supabase Storage

Amazon S3

Cloudflare R2

---

# Background Jobs

Future

Email sending

Notification processing

Payment verification

Report generation

Will be handled using workers.

---

# Scalability Strategy

Current

Single Backend

↓

Future

Microservices

↓

Containers

↓

Kubernetes

↓

Horizontal Scaling

No architectural changes should be required.

---

# Design Philosophy

Drawly prioritizes maintainability over premature optimization.

Simple solutions are preferred until complexity becomes necessary.

The architecture should evolve incrementally without sacrificing code quality.

---

# Architecture Goals

The architecture should allow future implementation of:

- Multi-tenancy
- Payment gateways
- Mobile applications
- Notifications
- Analytics
- Public APIs
- Team collaboration
- AI-powered features

without requiring a complete redesign.

---

# Guiding Principle

Every architectural decision must answer one question:

> Will this decision still make sense when Drawly has thousands of organizations and millions of tickets?

If the answer is yes, the decision is likely correct.