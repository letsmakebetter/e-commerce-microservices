# E-Commerce Microservices Platform

Initial repository structure for the SFWE415 Group 4 project. This `main` branch deliberately contains only the agreed project layout and coordination notes; implementation is developed in the member branches.

## Components

| Component | Planned technology | Owner branch |
| --- | --- | --- |
| User Profile | Python, FastAPI, PostgreSQL | `huseyin-burak-kasikci` |
| Product Catalog | Node.js, Express, MongoDB | `deniz-sismanyazici` |
| Search | Node.js, Elasticsearch | `deniz-sismanyazici` |
| Shopping Cart | Java, Spring Boot, Redis | `alim-ozgur-ozturk` |
| Web Interface | React, TypeScript/JavaScript, Material UI | `alim-ozgur-ozturk` |
| API Gateway and infrastructure | Shared, to be agreed by the team | shared review |

## Repository layout

```text
.
|-- api-gateway/
|-- cart-cna-microservice/
|-- docs/
|   |-- api-contracts/
|   `-- architecture/
|-- infra/
|   |-- docker/
|   `-- kubernetes/
|-- products-cna-microservice/
|-- search-cna-microservice/
|-- store-ui/
|   |-- public/
|   `-- src/
|-- users-cna-microservice/
`-- workflows/
```

## Collaboration rules

1. Work only in the branch assigned to you.
2. Do not commit `.env` files, credentials, generated build files, or local databases.
3. Open a pull request into `main` after the service is runnable and documented.
4. Put cross-service API contracts under `docs/api-contracts/` and infrastructure changes under `infra/`, after team review.

The team allocation follows the preliminary report and is subject to team-wide code review, integration, testing, documentation, and final-report work.
