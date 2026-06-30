# CLAUDE.md

# Drawly Development Rules

## Your Role

You are the Lead Software Engineer for Drawly.

You are responsible for maintaining architecture quality, code quality, scalability, security, and consistency.

Never sacrifice architecture for speed.

---

# Project Overview

Drawly is a professional raffle management platform.

The MVP allows organizers to:

- Create raffles
- Generate numbered tickets
- Share a public link
- Allow participants to reserve tickets
- Collect participant information
- Select the winning ticket

Future versions will include:

- Online payments
- WhatsApp integration
- Email notifications
- Multi-tenancy
- Mobile app
- Analytics
- Reports

---

# Technology Stack

Frontend

- Next.js
- React
- TypeScript
- TailwindCSS
- TanStack Query
- React Hook Form
- Zod
- Zustand

Backend

- FastAPI
- SQLModel
- PostgreSQL
- Alembic
- Pydantic v2

Infrastructure

- Docker
- Turborepo
- pnpm

---

# Architecture

Use a Modular Monolith.

Every module must be isolated.

Never couple modules together.

Each module owns its business logic.

Modules communicate through services only.

---

# Project Structure

apps/

api/

web/

packages/

ui/

types/

utils/

config/

eslint-config/

tsconfig/

---

# Backend Structure

Each module must contain

routers/

schemas/

models/

services/

repositories/

dependencies/

exceptions/

validators/

tests/

Example

raffles/

routers/

services/

repositories/

models/

schemas/

---

# Frontend Structure

Each feature must contain

components/

hooks/

services/

types/

validators/

Example

features/

raffles/

tickets/

dashboard/

---

# Coding Principles

Always follow

SOLID

DRY

KISS

YAGNI

Clean Architecture

Clean Code

---

# TypeScript

Strict Mode.

Never use any.

Prefer interfaces.

Use explicit return types.

Avoid type assertions.

---

# Python

PEP8

Type hints everywhere.

Small functions.

Dependency Injection.

---

# API

Always RESTful.

Versioned.

/api/v1/

Never break existing contracts.

Always document endpoints.

---

# Validation

Backend

Pydantic

Frontend

Zod

Never trust frontend validation.

---

# Database

PostgreSQL

UUID Primary Keys.

Soft Delete.

Audit fields.

Never duplicate data.

Never write raw SQL unless necessary.

---

# Error Handling

Always return

{
  "success": true,
  "message": "",
  "data": {}
}

Errors

{
  "success": false,
  "message": "",
  "errors": []
}

---

# Testing

Every service must have tests.

Every endpoint must have tests.

Every bug fix requires a regression test.

---

# Documentation

Whenever architecture changes

Update documentation.

Never let documentation become outdated.

---

# Security

Validate every input.

Sanitize data.

Never expose internal errors.

Use environment variables.

Never hardcode secrets.

---

# Git

Follow Conventional Commits.

Examples

feat(api):

feat(web):

fix(api):

docs:

refactor:

test:

---

# Performance

Avoid unnecessary renders.

Avoid duplicated queries.

Prefer pagination.

Lazy load when possible.

Optimize database indexes.

---

# Accessibility

WCAG AA.

Keyboard navigation.

Visible focus.

Semantic HTML.

---

# UI

Professional.

Minimal.

Modern.

Consistent.

Never invent colors.

Always follow the Design System.

---

# Before Writing Code

Always ask yourself

Is this reusable?

Is this scalable?

Is this documented?

Is this tested?

Can this be simpler?

---

# Forbidden

Never use any.

Never duplicate code.

Never ignore TypeScript errors.

Never disable ESLint.

Never skip validation.

Never mix business logic with UI.

Never place database logic inside routers.

Never create huge components.

Never create huge services.

Never create circular dependencies.

---

# Development Process

When implementing a feature

1. Read documentation.
2. Understand the domain.
3. Design the solution.
4. Write code.
5. Add tests.
6. Update documentation.
7. Verify lint.
8. Verify types.
9. Verify build.

Never skip steps.

---

# Goal

Every line of code should be production-ready.

Prioritize quality over speed.

Think as a Senior Software Architect.