# 🎟️ Drawly

> **Modern Raffle Management Platform**

Drawly is a modern, scalable platform for creating, managing, and tracking numbered raffles.

Built with scalability in mind, Drawly enables organizers to create raffles, automatically generate numbered tickets, manage participants, monitor ticket availability in real time, and select winners through a clean and intuitive dashboard.

The project is designed following modern software architecture principles and is intended to evolve into a complete SaaS platform, supporting online payments, multiple organizations, notifications, analytics, mobile applications, and public APIs.

---

# ✨ Features

## Current MVP

- Create, edit, publish, and close raffles
- Automatic numbered ticket generation
- Public raffle pages
- Real-time ticket availability
- Participant registration
- Winner selection
- Dashboard with raffle statistics
- Responsive interface
- RESTful API
- Dockerized development environment

---

# 🚀 Future Features

- Online payments
- QR code generation
- Email notifications
- WhatsApp notifications
- Multi-tenant architecture
- User authentication
- Role-based permissions
- Mobile application
- Reports and analytics
- AI-powered insights
- Public API
- Webhooks
- Internationalization (i18n)

---

# 🏗️ Project Architecture

Drawly follows a **Modular Monolith Architecture**, designed to evolve into a microservices architecture if needed.

The project is organized as a monorepo.

```
drawly/

├── apps/
│   ├── api/
│   └── web/
│
├── packages/
│   ├── ui/
│   ├── utils/
│   ├── config/
│   └── types/
│
├── docs/
│
├── docker/
│
└── .github/
```

---

# 🛠️ Tech Stack

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Query
- React Hook Form
- Zustand
- Zod

## Backend

- FastAPI
- Python
- SQLModel
- Alembic

## Database

- PostgreSQL

## Infrastructure

- Docker
- Docker Compose

---

# 📂 Documentation

Project documentation is available inside the `docs` directory.

```
docs/

01-product/
02-architecture/
03-database/
04-api/
05-design/
06-roadmap/
07-development/
08-decisions/
```

---

# 🎯 Project Goals

The main goal of Drawly is to provide an easy, secure, and scalable way to manage numbered raffles.

The application is being developed with long-term scalability in mind, ensuring that future features can be added without requiring major architectural changes.

---

# 📅 Development Roadmap

- Foundation
- Architecture
- Infrastructure
- Backend
- Frontend
- Integration
- Testing
- Deployment
- SaaS Features

Detailed roadmap is available in:

```
docs/06-roadmap/ROADMAP.md
```

---

# 📖 Development Principles

The project follows:

- Clean Architecture
- SOLID Principles
- DRY
- KISS
- Feature-based organization
- Strict typing
- Domain-driven thinking
- Component reusability

---

# 🤝 Contributing

Although Drawly is currently maintained by a single developer, the project follows collaborative development standards to make future contributions easier.

---

# 📄 License

License information will be defined before the first public release.

---

# 👨‍💻 Author

Developed by **Sebastian Saldarriaga**.