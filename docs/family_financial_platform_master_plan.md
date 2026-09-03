# Family Financial Management Platform --- Master Product & Technical Plan

## 1. Purpose

Build a secure, cloud-hosted family financial management platform that
provides a unified view of a household's finances and allows household
members to interact with their financial data through both a web
dashboard and an LLM-powered conversational interface.

The platform is designed for two partners who each authenticate with
their own Google account and join the same Household. All information
inside a Household is visible and editable by both members, while
financial records retain ownership metadata so the system can
distinguish between Partner A, Partner B, and shared finances.

The long-term system should support automatic financial integrations
where practical and document/manual ingestion where direct integrations
are unavailable.

The system must be extensible: new financial source types, account
types, document types, LLM providers, embedding providers, and
integrations should be addable without redesigning the core
architecture.

------------------------------------------------------------------------

## 2. Product Goals

The platform should answer four fundamental questions:

1.  What do we own and owe right now?
2.  How has our financial position changed over time?
3.  Where does our money come from and where does it go?
4.  Can we ask arbitrary questions about our financial history and
    receive grounded answers, calculations, and visualizations?

Core capabilities:

-   Household-level financial dashboard
-   Per-partner financial breakdown
-   Net worth tracking
-   Income and expense tracking
-   Bank account tracking
-   Credit-card expense ingestion
-   Cash transaction entry
-   Gift-card / stored-value balance tracking such as BuyMe
-   Brokerage account tracking
-   Crypto account tracking
-   Pension tracking
-   Study fund / Keren Hishtalmut tracking
-   Investment property tracking
-   Mortgage tracking
-   Gemach and other loan tracking
-   Recurring expense/income classification
-   Document ingestion
-   AI-assisted extraction and classification
-   Human review before extracted data becomes authoritative
-   Semantic document search / RAG
-   LLM-powered financial Q&A
-   On-demand chart generation
-   Telegram interface
-   Google authentication
-   Cloud deployment
-   CI/CD from the first implementation

Budget planning is explicitly out of scope for the current product
vision.

------------------------------------------------------------------------

# 3. Core Product Principles

## 3.1 Household Is the Main Tenant

The main isolation boundary is a `Household`.

A Household contains up to two partner users for the initial
implementation.

Each user has an individual Google-authenticated identity.

Financial data may be marked as:

-   owned by Partner A
-   owned by Partner B
-   shared

Both members of the Household can view, edit, and delete all Household
financial data.

Ownership is for analytics and reporting, not privacy between partners.

------------------------------------------------------------------------

## 3.2 Preserve Source Data

Never discard original financial information.

For every imported document or source payload, preserve where
applicable:

-   original file
-   original metadata
-   parsed text
-   OCR output
-   extracted structured representation
-   extraction result
-   approved database records
-   relationship between records and their source
-   processing status
-   processing errors

This allows the system to reprocess historical documents when parsers,
prompts, schemas, or models improve.

------------------------------------------------------------------------

## 3.3 Human-in-the-Loop Ingestion

Automatically extracted financial information must never immediately
become authoritative financial data.

Pipeline:

`Input -> Parse -> Extract -> Classify -> Detect Duplicates -> Pending Review -> User Approval -> Canonical Database`

The user must approve extracted records.

The review interface must allow:

-   editing records
-   changing category
-   changing subcategory
-   changing ownership
-   changing recurring status
-   deleting proposed records
-   approving individual records
-   approving multiple records
-   approving an entire batch

Review must be possible through the web application and, where
practical, through Telegram.

------------------------------------------------------------------------

## 3.4 Deterministic Financial Logic

The LLM must not be responsible for arithmetic or authoritative
financial calculations.

The LLM should:

-   understand user intent
-   select tools
-   determine parameters
-   explain results
-   suggest visualizations

Backend services should perform:

-   aggregations
-   sums
-   filtering
-   net worth calculations
-   date comparisons
-   ownership breakdowns
-   asset/liability calculations
-   chart datasets

------------------------------------------------------------------------

## 3.5 Provider Independence

Do not couple application logic directly to a specific LLM or embedding
provider.

Define interfaces such as:

``` python
class LLMProvider:
    async def generate(...)
    async def tool_call(...)

class EmbeddingProvider:
    async def embed_documents(...)
    async def embed_query(...)
```

Initial providers may use OpenAI, Anthropic, or another suitable API.

Provider selection should be configuration-driven.

------------------------------------------------------------------------

# 4. Users and Authentication

## 4.1 Authentication

Initial authentication method:

-   Google OAuth / OpenID Connect

No username/password authentication is required for the initial
implementation.

## 4.2 Household Creation

Flow:

1.  User signs in with Google.
2.  User creates a Household or accepts an invitation.
3.  Household creator receives an invitation mechanism/link.
4.  Second partner signs in with Google.
5.  Second partner joins the Household.
6.  Both users now access the same financial workspace.

A user must never access another Household without explicit membership.

## 4.3 Household Context

Every relevant database query must be scoped by `household_id`.

Do not rely on frontend filtering for tenant isolation.

------------------------------------------------------------------------

# 5. Financial Domain Model

The core database should not be designed around specific banks or
financial institutions.

External sources should map into a generic canonical financial model.

## 5.1 Financial Accounts

Generic account representation.

Example account types:

-   bank
-   credit_card
-   cash
-   gift_card
-   brokerage
-   crypto
-   pension
-   study_fund
-   other

Suggested fields:

``` text
id
household_id
owner_user_id nullable
ownership_type
account_type
name
institution_name
external_reference nullable
current_value_ils
active
created_at
updated_at
```

`ownership_type`:

-   PERSONAL
-   SHARED

------------------------------------------------------------------------

# 6. Transactions

Transactions are one of the central entities in the system.

Suggested fields:

``` text
id
household_id
owner_user_id nullable
account_id nullable
transaction_type
amount_ils
original_amount nullable
original_currency nullable
exchange_rate nullable
transaction_date
merchant nullable
description nullable
category_id nullable
subcategory_id nullable
recurrence_type
source_type
source_document_id nullable
source_record_reference nullable
created_at
updated_at
```

## 6.1 Transaction Types

At minimum:

-   EXPENSE
-   INCOME
-   INTERNAL_TRANSFER

Internal transfers must not affect household income/expense analytics.

Examples:

-   bank -\> brokerage
-   bank -\> partner bank account
-   bank -\> cash
-   credit-card settlement where underlying card purchases are already
    recorded

## 6.2 Recurrence

Every income and expense should contain:

``` text
recurrence_type = RECURRING | ONE_TIME
```

The LLM/extraction system may suggest this value, but the user confirms
it during ingestion review.

------------------------------------------------------------------------

# 7. Categories and Subcategories

The application ships with a default category taxonomy.

Users can:

-   add categories
-   add subcategories
-   rename categories
-   modify classification

Example:

``` text
Food
  Grocery
  Restaurants
  Delivery
```

Merchant-based learned rules should be supported.

Example:

``` text
merchant pattern: "Osher Ad"
category: Food
subcategory: Grocery
```

The system should use:

1.  deterministic merchant rules
2.  historical classifications
3.  LLM classification where needed

A user correction may optionally create/update a merchant classification
rule.

------------------------------------------------------------------------

# 8. Income

Income uses the same canonical transaction infrastructure.

Initial income categories may include:

-   salary
-   rental income
-   dividends
-   interest
-   tax refund
-   gift
-   reimbursement
-   investment proceeds
-   other

Users must be able to create additional income categories and sources.

Income must retain ownership so salary and other income can be analyzed
per partner.

------------------------------------------------------------------------

# 9. Duplicate Detection

Duplicate detection happens before approval.

Signals may include:

-   transaction date
-   amount
-   account/source
-   merchant
-   description similarity
-   external transaction ID
-   source document
-   normalized merchant name

Example:

``` text
Existing:
2026-06-01 | Osher Ad Ltd | 326.70

Proposed:
2026-06-01 | Osher Ad | 326.70
```

The review interface should display a duplicate warning and the existing
matching record.

The user chooses whether to:

-   reject the proposed duplicate
-   keep it
-   resolve/merge where supported

Document-level duplicate detection must also exist so uploading the same
file twice does not silently duplicate its contents.

Use file hashes as one strong signal.

------------------------------------------------------------------------

# 10. Investment Accounts

Initial investment tracking is intentionally account-level rather than
security-level.

For each brokerage or crypto account store:

-   institution/account name
-   owner
-   current total value in ILS
-   asset allocation

Initial allocation types:

-   stocks
-   bonds
-   money-market funds
-   crypto
-   cash
-   other

Individual stock/security transaction tracking is not required for the
first product scope.

Example:

``` text
IBKR
Total: 250,000 ILS

Stocks: 180,000
Bonds: 30,000
Money Market: 40,000
```

------------------------------------------------------------------------

# 11. Currency

The product's canonical reporting currency is ILS.

All dashboards and aggregate calculations are shown in ILS.

When imported data originates in another currency, preserve:

``` text
original_currency
original_amount
exchange_rate
amount_ils
```

This allows future auditing and recalculation.

------------------------------------------------------------------------

# 12. Pension and Study Funds

Supported product types should include:

-   pension
-   study fund / Keren Hishtalmut
-   extensible future retirement/savings products

Store:

-   owner
-   managing institution
-   product type
-   current value
-   monthly contribution
-   employee contribution where applicable
-   employer contribution where applicable
-   investment track
-   value snapshots

Examples of investment tracks:

-   S&P 500
-   equity
-   general
-   other

Detailed performance benchmarking is not required initially.

------------------------------------------------------------------------

# 13. Investment Property

Each property should be represented as a dedicated domain object.

Store:

``` text
id
household_id
name
address
ownership
current_estimated_value
linked_mortgage_id nullable
```

Track property-related income:

-   rent
-   other property income

Track property-related expenses:

-   building committee / HOA
-   municipal tax / Arnona
-   insurance
-   repairs
-   renovations
-   legal expenses
-   brokerage expenses
-   other

The system should calculate property cash flow:

`Property Cash Flow = Property Income - Property Expenses`

Mortgage payments should be modeled carefully to avoid double counting
where appropriate.

Full ROI/yield analytics are not a required initial feature.

------------------------------------------------------------------------

# 14. Mortgage

The mortgage module should support:

-   current remaining balance
-   monthly payment
-   linked property
-   multiple mortgage tracks
-   uploaded mortgage reports

Mortgage track fields may include:

``` text
track_type
original_principal
remaining_principal
interest_type
interest_rate
linked_index
start_date
end_date
```

Examples:

-   Prime
-   fixed unlinked
-   variable
-   other

The user should be able to upload a mortgage statement and have the
ingestion pipeline extract proposed mortgage data.

An amortization schedule does not need to be permanently visible on the
dashboard.

It should be generated/retrieved on demand when requested through the UI
or AI interface.

------------------------------------------------------------------------

# 15. Loans / Gemach

The liability model must be extensible.

Initial liability types:

-   mortgage
-   Gemach loan
-   bank loan
-   personal loan
-   other

Suggested fields:

``` text
original_amount
remaining_balance
monthly_payment nullable
lender
start_date nullable
end_date nullable
owner
```

------------------------------------------------------------------------

# 16. Net Worth

Canonical formula:

`Net Worth = Total Assets - Total Liabilities`

The system must support:

## Current Net Worth

Overall Household net worth.

## Historical Net Worth

Net worth by month and over arbitrary date ranges.

## Asset-Type Breakdown

Examples:

-   real estate
-   banks/cash
-   brokerage
-   crypto
-   pension
-   study funds
-   gift cards
-   other

## Liability Breakdown

Examples:

-   mortgage
-   Gemach
-   other loans

------------------------------------------------------------------------

# 17. Historical Snapshots

Never overwrite the only copy of a changing asset value.

Maintain snapshots:

``` text
entity_id
entity_type
snapshot_date
value_ils
source
```

Examples:

-   bank balance
-   brokerage balance
-   crypto account value
-   pension value
-   study fund value
-   property estimated value
-   mortgage remaining balance

Snapshots enable questions such as:

-   What was our net worth six months ago?
-   How much did our pension assets grow this year?
-   Plot our net worth for the last two years.

------------------------------------------------------------------------

# 18. Data Ingestion

The system must support multiple ingestion mechanisms.

## 18.1 Automatic Integrations

Where APIs or appropriate integrations exist, implement source adapters.

Conceptual interface:

``` python
class FinancialSourceAdapter:
    async def sync(...)
    async def normalize(...)
```

Adapters should normalize external source data into canonical proposed
records.

## 18.2 File Upload

Support at minimum:

-   PDF
-   CSV
-   XLSX
-   images/screenshots

Examples:

-   bank statement
-   credit-card statement
-   pension statement
-   mortgage report
-   investment account statement
-   receipt

## 18.3 Manual Forms

Users can manually add/edit:

-   transactions
-   balances
-   accounts
-   liabilities
-   property information
-   investment account values
-   other financial information

## 18.4 AI Chat Entry

Example:

> I paid 80 ILS cash for groceries today.

The AI parses the request and creates a pending proposed transaction.

It does not immediately commit it as an approved transaction.

## 18.5 Telegram Entry

Telegram should expose the same financial actions through the shared
backend.

------------------------------------------------------------------------

# 19. Document Processing Pipeline

Recommended pipeline:

``` text
Upload
  |
  v
Object Storage
  |
  v
Document Registration
  |
  v
Duplicate Check
  |
  v
Document Type Detection
  |
  v
Parser / OCR
  |
  v
Normalized Text
  |
  +----------------------+
  |                      |
  v                      v
Structured Extraction    Chunking
  |                      |
  v                      v
Classification           Embeddings
  |                      |
  v                      v
Pending Records          Vector Store
  |
  v
Duplicate Detection
  |
  v
Review
  |
  v
Approval
  |
  v
Canonical Financial DB
```

Document processing should be asynchronous.

A worker/queue architecture should be used so long-running OCR,
extraction, and embedding jobs do not block HTTP requests.

------------------------------------------------------------------------

# 20. Document Storage and RAG

Every supported document should be searchable later.

Store:

-   original document
-   parsed text
-   chunks
-   embeddings
-   metadata

Important metadata:

``` text
household_id
owner_user_id
document_type
institution
document_date
period_start
period_end
source
account_id
property_id
mortgage_id
```

Semantic search must always be filtered by `household_id`.

Future RAG should support questions such as:

-   Find the mortgage report that mentioned a specific track.
-   Find documents containing purchases from a merchant.
-   What did my January mortgage statement say?
-   Find the receipt for a property repair.

Where technically possible, answers should retain references to the
originating document and relevant page/chunk.

------------------------------------------------------------------------

# 21. AI Architecture

Use one shared AI backend for both Web Chat and Telegram.

``` text
Web Chat --------\
                  \
                   -> Financial AI Service -> Tools -> Domain Services -> DB
                  /
Telegram --------/
```

Avoid creating separate business logic for Telegram.

## 21.1 Agent Responsibilities

The AI layer should:

1.  understand the request
2.  resolve dates/entities/categories
3.  choose an approved tool
4.  call the tool
5.  interpret structured output
6.  answer the user
7.  suggest relevant visualizations

Do not give the LLM unrestricted database access.

------------------------------------------------------------------------

# 22. AI Tools

Initial tool families:

## Transactions

``` text
search_transactions
aggregate_expenses
aggregate_income
get_recurring_transactions
compare_periods
get_category_breakdown
```

## Net Worth

``` text
get_current_net_worth
get_net_worth_history
get_asset_breakdown
get_liability_breakdown
```

## Accounts

``` text
get_accounts
get_account_balance
get_account_history
```

## Investments

``` text
get_investment_accounts
get_investment_allocation
```

## Property

``` text
get_property_summary
get_property_income
get_property_expenses
get_property_cash_flow
```

## Mortgage

``` text
get_mortgage_summary
get_mortgage_tracks
generate_amortization_schedule
```

## Documents

``` text
search_documents
get_document
search_document_chunks
```

## Visualization

``` text
suggest_charts
generate_chart
```

All tools must enforce Household authorization independently of the LLM.

------------------------------------------------------------------------

# 23. Visualization Architecture

Charts are generated by deterministic application code, not by the LLM
itself.

Example conversation:

User:

> How much did we spend on food during the last two years?

Backend returns structured analytics.

AI responds with the result and may suggest:

-   monthly trend
-   yearly comparison
-   breakdown by subcategory
-   breakdown by partner

The user may then request:

> Show monthly trend.

The LLM calls the chart tool with a validated chart specification.

Suggested chart specification:

``` json
{
  "chart_type": "line",
  "metric": "expenses",
  "group_by": "month",
  "filters": {
    "category": "food"
  },
  "date_range": {
    "start": "2024-09-01",
    "end": "2026-09-01"
  }
}
```

The backend generates/returns chart-ready data.

The web UI renders an interactive chart.

Telegram may render a chart image.

------------------------------------------------------------------------

# 24. Telegram

Telegram is an alternative interface to the same backend.

Initial capabilities:

-   ask financial questions
-   receive financial answers
-   request charts
-   enter transactions
-   review/approve pending ingestion where practical

No proactive notifications are required initially.

## Telegram Security

A Telegram identity must be explicitly linked to an authenticated
application user.

Never authorize a Telegram request merely because the bot received a
message.

Store a verified mapping:

``` text
telegram_user_id -> application_user_id -> household_id
```

------------------------------------------------------------------------

# 25. Web Application

The web application should contain:

``` text
/dashboard
/transactions
/accounts
/investments
/property
/mortgage
/pension
/documents
/review
/chat
/settings
```

The AI chat should be accessible from the web application and may be
implemented as a persistent side panel or dedicated page.

------------------------------------------------------------------------

# 26. Home Dashboard

Initial dashboard widgets:

## Net Worth

-   current total
-   historical trend

## Banks / Cash

-   current liquid balances

## Investments

-   brokerage
-   crypto
-   pension
-   study funds

## Liabilities

-   mortgage
-   Gemach
-   other loans

## Income vs Expenses

-   current month
-   historical comparison

## Expense Breakdown

-   category
-   subcategory

## Household Breakdown

-   Partner A
-   Partner B
-   shared

## Investment Property

-   estimated value
-   mortgage balance
-   rent
-   expenses
-   net cash flow

## Recent Activity

-   recent approved transactions

## Pending Review

-   batches/records waiting for user approval

------------------------------------------------------------------------

# 27. Review UI

The primary review interface is a table.

Columns should adapt to the record type.

For transactions:

``` text
Approve
Date
Merchant
Description
Amount
Type
Category
Subcategory
Owner
Recurring
Source
Duplicate Warning
```

Actions:

-   inline edit
-   approve selected
-   reject selected
-   approve all
-   filter warnings/errors
-   inspect source document

------------------------------------------------------------------------

# 28. Editing and Deletion

After approval, both Household members may edit and delete records.

The initial product does not require a business-level audit history of
previous field values.

The current authoritative state is sufficient.

However, source provenance must remain available.

------------------------------------------------------------------------

# 29. Data Provenance

Every automatically imported record should retain enough information to
explain its origin.

Example:

``` text
source_type = DOCUMENT
source_document_id = ...
source_record_reference = ...
```

For integrations:

``` text
source_type = API
source_integration_id = ...
external_record_id = ...
```

For manual input:

``` text
source_type = MANUAL
created_by_user_id = ...
```

This is distinct from an audit log.

------------------------------------------------------------------------

# 30. Suggested Technology Stack

## Frontend

Recommended:

-   Next.js
-   TypeScript
-   React
-   Tailwind CSS
-   component library such as shadcn/ui
-   Recharts or another mature React chart library

## Backend

Recommended:

-   Python
-   FastAPI
-   Pydantic
-   SQLAlchemy 2.x
-   Alembic

## Database

-   PostgreSQL

## Vector Search

For the prototype:

-   PostgreSQL + pgvector

Avoid introducing a separate vector database until scale or
functionality justifies it.

## Async Jobs

Prototype options:

-   Redis-backed queue + worker
-   or a cloud-native background worker supported by the deployment
    platform

Keep the worker interface abstract enough to replace later.

## Object Storage

Use S3-compatible object storage for original documents.

Do not store large PDFs/images directly inside PostgreSQL.

## AI

Provider abstraction supporting interchangeable LLMs.

## Embeddings

Provider abstraction + pgvector.

## Telegram

Telegram Bot API integrated with the backend.

------------------------------------------------------------------------

# 31. Repository Architecture

A monorepo is recommended for the initial product.

``` text
financial-platform/
|
├── apps/
│   ├── web/
│   └── api/
|
├── workers/
│   └── document_worker/
|
├── packages/
│   └── shared/
|
├── infra/
|
├── docs/
|
├── .github/
│   └── workflows/
|
├── docker-compose.yml
└── README.md
```

Backend structure:

``` text
apps/api/app/
├── api/
├── auth/
├── db/
├── models/
├── schemas/
├── services/
│   ├── transactions/
│   ├── accounts/
│   ├── net_worth/
│   ├── documents/
│   ├── investments/
│   ├── mortgage/
│   └── property/
├── ai/
│   ├── agent/
│   ├── tools/
│   ├── providers/
│   └── prompts/
├── ingestion/
│   ├── parsers/
│   ├── extractors/
│   ├── classifiers/
│   └── adapters/
└── integrations/
    └── telegram/
```

------------------------------------------------------------------------

# 32. API Design

Use REST APIs initially.

Example resources:

``` text
/api/v1/households
/api/v1/accounts
/api/v1/transactions
/api/v1/categories
/api/v1/assets
/api/v1/liabilities
/api/v1/properties
/api/v1/mortgages
/api/v1/pensions
/api/v1/documents
/api/v1/ingestion-batches
/api/v1/reviews
/api/v1/chat
/api/v1/charts
/api/v1/integrations
```

All endpoints must derive authorized Household scope from the
authenticated user.

Never accept an arbitrary `household_id` and trust it without membership
validation.

------------------------------------------------------------------------

# 33. Security Requirements

Financial information is sensitive.

Minimum requirements from the prototype:

-   HTTPS only in production
-   Google OAuth
-   secure session handling
-   Household-level authorization
-   secrets stored as environment/platform secrets
-   no secrets committed to Git
-   database encryption at rest where provided by infrastructure
-   object-storage access restricted
-   signed/temporary document URLs
-   strict file upload limits
-   MIME/type validation
-   protection against malicious uploads
-   parameterized SQL / ORM
-   rate limiting for expensive AI endpoints
-   AI tool authorization
-   sanitized logs
-   never log raw financial documents or credentials
-   backup strategy

Do not expose PostgreSQL publicly unless required.

------------------------------------------------------------------------

# 34. CI/CD From Day One

CI/CD is part of the first implementation, not a later improvement.

Source control:

-   GitHub

Recommended workflow:

``` text
Developer
   |
git push / pull request
   |
GitHub
   |
GitHub Actions
   |
   +-- lint
   +-- type checks
   +-- backend tests
   +-- frontend tests
   +-- build
   |
merge to main
   |
deploy
   |
Cloud Environment
   |
Public HTTPS URL
```

Database migrations must be integrated into the deployment process with
safe migration practices.

Pull requests should fail if required checks fail.

------------------------------------------------------------------------

# 35. Initial Cloud Strategy

Primary objective:

-   inexpensive
-   simple
-   managed
-   public HTTPS URL
-   Git-friendly deployment
-   easy to replace later

For the first prototype, use a simple managed application platform such
as Render or an equivalent current low-cost provider rather than
starting with Kubernetes or complex AWS infrastructure.

The architecture must remain portable:

-   Dockerized backend
-   standard PostgreSQL
-   S3-compatible object storage
-   environment-based configuration
-   no unnecessary provider-specific business logic

This enables later migration to AWS, GCP, Azure, or another provider.

The exact hosting provider and plan should be revalidated against
current pricing immediately before deployment.

------------------------------------------------------------------------

# 36. Environments

At minimum:

## Local

Docker Compose:

-   PostgreSQL
-   pgvector
-   optional Redis
-   API
-   web

## Production

Cloud deployment reachable via public HTTPS URL.

A staging environment can be added after the prototype when needed.

------------------------------------------------------------------------

# 37. Testing Strategy

## Backend Unit Tests

Test:

-   transaction classification helpers
-   internal transfer behavior
-   net worth calculations
-   property cash flow
-   duplicate detection
-   category rules
-   snapshot calculations

## Integration Tests

Test:

-   authentication boundaries
-   Household isolation
-   document ingestion
-   approval workflow
-   database persistence
-   AI tool execution

## AI Evaluation Tests

Maintain a small evaluation dataset.

Examples:

``` text
"How much did we spend on groceries last month?"
"Show our net worth over the last year."
"How much money is currently invested in crypto?"
"What are our recurring expenses?"
```

Evaluate:

-   correct tool selection
-   correct parameters
-   correct Household scope
-   grounded response
-   no fabricated financial values

## End-to-End Tests

Critical flow:

`Login -> Upload -> Extraction -> Review -> Approval -> Dashboard -> Ask AI -> Generate Chart`

------------------------------------------------------------------------

# 38. Observability

From the prototype, use structured logging.

Track document processing stages:

``` text
uploaded
classified
parsed
extracted
embedded
awaiting_review
approved
failed
```

Track AI calls:

-   provider
-   model
-   latency
-   tool calls
-   token usage where available
-   errors

Do not log sensitive raw content unnecessarily.

------------------------------------------------------------------------

# 39. Prototype Scope

The first prototype should prove a complete vertical slice rather than
implementing every financial integration.

## Prototype Success Flow

A user should be able to:

1.  Open the public website.
2.  Sign in with Google.
3.  Create a Household.
4.  Invite/link the second partner.
5.  Create financial accounts.
6.  Add a transaction manually.
7.  Upload at least one representative financial statement.
8.  Have the document processed.
9.  See proposed extracted records.
10. Review/edit them in a table.
11. Approve them.
12. See approved data reflected in the dashboard.
13. Ask the LLM a question about the data.
14. Have the LLM call a controlled financial tool.
15. Receive a grounded answer.
16. Request/select a visualization.
17. See a generated chart.
18. Access the same AI backend through Telegram.
19. Push code to Git and automatically deploy the application.
20. Access the deployed application through a public HTTPS URL.

This is the first major milestone.

------------------------------------------------------------------------

# 40. Prototype Implementation Phases

## Phase 0 --- Repository and Engineering Foundation

Create:

-   monorepo
-   frontend
-   FastAPI backend
-   PostgreSQL
-   migrations
-   Docker Compose
-   linting
-   formatting
-   testing
-   environment configuration
-   GitHub Actions
-   initial cloud deployment

Definition of done:

A trivial authenticated or health-check version of frontend/backend is
deployed through CI/CD and reachable through HTTPS.

------------------------------------------------------------------------

## Phase 1 --- Authentication and Household

Implement:

-   Google login
-   user persistence
-   Household creation
-   invitation/join flow
-   authorization middleware
-   Household-scoped repository/service patterns

Tests must prove one Household cannot access another.

------------------------------------------------------------------------

## Phase 2 --- Financial Core

Implement:

-   accounts
-   categories
-   subcategories
-   transactions
-   income/expense/internal transfer
-   ownership
-   recurring/one-time
-   manual CRUD
-   default categories
-   merchant classification rules

------------------------------------------------------------------------

## Phase 3 --- Dashboard Foundation

Implement:

-   current income
-   current expenses
-   category breakdown
-   ownership breakdown
-   accounts
-   recent transactions

Add chart components that will later also be reusable by AI-generated
chart specifications.

------------------------------------------------------------------------

## Phase 4 --- Assets, Liabilities, and Snapshots

Implement:

-   generic assets/liabilities where needed
-   brokerage account values
-   crypto values
-   pension
-   study funds
-   loans
-   snapshots
-   current net worth
-   historical net worth

------------------------------------------------------------------------

## Phase 5 --- Property and Mortgage

Implement:

-   property model
-   property income/expenses
-   property cash flow
-   mortgage
-   mortgage tracks
-   property/mortgage linkage

------------------------------------------------------------------------

## Phase 6 --- Document Infrastructure

Implement:

-   object storage
-   document metadata
-   upload API
-   file hashing
-   duplicate document detection
-   processing statuses
-   asynchronous worker
-   parser interface
-   extraction interface

Start with one representative statement format rather than attempting
every bank/card format immediately.

------------------------------------------------------------------------

## Phase 7 --- Extraction Review

Implement:

-   extraction schema
-   pending records
-   duplicate transaction detection
-   review table
-   edit/reject/approve
-   batch approval
-   provenance links

No extracted financial record bypasses review.

------------------------------------------------------------------------

## Phase 8 --- Embeddings and Document Search

Implement:

-   normalized document text
-   chunking strategy
-   embedding provider interface
-   pgvector
-   metadata-filtered semantic retrieval
-   Household isolation
-   document search API
-   source references

------------------------------------------------------------------------

## Phase 9 --- Financial AI

Implement:

-   LLM provider abstraction
-   agent/orchestrator
-   financial tool registry
-   tool authorization
-   structured tool outputs
-   conversational context

Start with deterministic tools rather than Text-to-SQL.

The AI should call domain-level tools such as `aggregate_expenses`, not
generate arbitrary SQL.

------------------------------------------------------------------------

## Phase 10 --- AI Charts

Implement:

-   chart suggestion schema
-   validated chart specification
-   chart data service
-   reusable web renderer
-   conversational follow-up

Flow:

`Question -> Financial Tool -> Answer -> Chart Suggestions -> User Selection -> Chart Tool -> Render`

------------------------------------------------------------------------

## Phase 11 --- Telegram

Implement:

-   Telegram bot
-   account linking
-   user authorization
-   financial Q&A
-   manual transaction proposal
-   chart image generation
-   review/approval workflow where practical

Reuse the same domain services and AI orchestration as the web
application.

------------------------------------------------------------------------

## Phase 12 --- Hardening

Implement/improve:

-   rate limiting
-   file security
-   error handling
-   retries
-   backups
-   observability
-   AI evaluations
-   E2E tests
-   responsive/mobile UI
-   production documentation

------------------------------------------------------------------------

# 41. Recommended First Vertical Slice for a Coding Agent

The coding agent should not begin by implementing every entity.

Implement this exact end-to-end path first:

``` text
Google Login
    ↓
Household
    ↓
Manual Account
    ↓
Upload Credit-Card Statement
    ↓
Store Original File
    ↓
Extract Transactions
    ↓
Classify Category/Subcategory
    ↓
Duplicate Detection
    ↓
Pending Review Table
    ↓
User Approval
    ↓
Canonical Transactions
    ↓
Dashboard Expense Chart
    ↓
LLM Question
    ↓
aggregate_expenses Tool
    ↓
Answer
    ↓
Chart Suggestion
    ↓
Generated Chart
```

Once this works in production through CI/CD, expand horizontally into
pensions, investments, mortgage, property, and additional document
adapters.

------------------------------------------------------------------------

# 42. Important Implementation Constraints for the Coding Agent

1.  Do not bypass the service/domain layer from AI tools.
2.  Do not give the LLM unrestricted SQL execution.
3.  Do not make financial arithmetic dependent on an LLM response.
4.  Do not insert extracted document records directly into canonical
    tables.
5.  Do not discard source files after extraction.
6.  Do not overwrite historical asset values; create snapshots.
7.  Do not count internal transfers as income or expenses.
8.  Do not hard-code financial institutions into the core schema.
9.  Do not couple business logic to one LLM provider.
10. Do not couple document search to one embedding model.
11. Do not authorize resources based only on IDs supplied by the client.
12. Every data access operation must enforce Household membership.
13. All production secrets must remain outside the repository.
14. CI/CD must exist before substantial feature development.
15. The production application must remain deployable through standard
    containers and managed services.

------------------------------------------------------------------------

# 43. Initial Non-Goals

Not required in the initial implementation:

-   household budgeting
-   automatic proactive Telegram notifications
-   detailed security-level stock portfolio analytics
-   sophisticated investment performance attribution
-   direct dashboard display of full mortgage amortization schedules
-   transaction installment linking
-   refund-to-original-transaction linking
-   detailed business audit history
-   Kubernetes
-   microservices

These may be added later without redefining the core product.

------------------------------------------------------------------------

# 44. Future Extensions

The architecture should leave room for:

-   Israeli open-banking integrations
-   credit-card integrations
-   brokerage APIs
-   crypto exchange APIs
-   email statement ingestion
-   automatic recurring transaction detection
-   smarter anomaly detection
-   financial forecasting
-   tax-related analytics
-   richer investment analytics
-   document reprocessing with newer models
-   additional Household members/roles
-   proactive alerts
-   mobile application
-   advanced financial planning

------------------------------------------------------------------------

# 45. Definition of Product Success

The target experience is:

A household member opens one application and sees a reliable, historical
picture of the family's assets, liabilities, income, expenses,
investments, pensions, property, mortgage, and other financial sources.

When automatic integrations exist, data can be synchronized.

When they do not, the user can upload a document, screenshot,
spreadsheet, enter information manually, or describe it
conversationally.

The system understands the input, preserves the original source,
extracts structured information, detects likely duplicates, proposes
categories and ownership, and asks for approval before updating
authoritative financial data.

The user can then ask natural-language questions about the entire
Household financial history. The LLM uses controlled tools over
canonical data and document retrieval, returns grounded answers,
suggests useful visualizations, and generates requested charts.

The same capabilities are accessible from the web application and
Telegram.

The system is deployed from Git through CI/CD to a low-cost cloud
environment and is accessible through a secure public URL that both
partners can use. ---

# 46. Repository, Runtime, and Development Standards

This section is normative for the initial implementation. The coding
agent should follow these choices unless a concrete incompatibility is
discovered.

## 46.1 Git Repository

Canonical repository:

``` text
https://github.com/ruvicohen/financial_managed.git
```

Repository name:

``` text
financial_managed
```

Default branch:

``` text
main
```

The repository should remain a monorepo for the initial implementation.

Clone example:

``` bash
git clone https://github.com/ruvicohen/financial_managed.git
cd financial_managed
```

## 46.2 Git Workflow

Use short-lived feature branches.

Naming examples:

``` text
feat/google-auth
feat/household-model
feat/document-ingestion
fix/duplicate-detection
chore/ci
```

Normal development flow:

``` text
main
  |
  +-- feature branch
        |
        +-- commits
        |
        +-- pull request
              |
              +-- CI checks
              |
              +-- merge to main
                    |
                    +-- production deployment
```

Do not develop long-running unrelated work directly on `main`.

For the prototype, prefer squash merging so `main` remains readable.

## 46.3 Commit Convention

Use Conventional Commits.

Examples:

``` text
feat: add household creation flow
fix: prevent duplicate statement ingestion
chore: configure backend linting
test: add net worth service tests
docs: update local development instructions
refactor: extract llm provider interface
ci: add production deployment workflow
```

Common prefixes:

``` text
feat
fix
refactor
test
docs
chore
ci
build
perf
```

## 46.4 Main Branch Protection

Configure `main` as a protected branch when repository settings allow
it.

Target rules:

-   prevent force pushes
-   prevent branch deletion
-   require pull requests for normal development
-   require CI status checks before merge
-   require conversations to be resolved
-   do not merge known failing builds

For a solo prototype, mandatory human approval is optional because it
can unnecessarily block the developer. CI checks are mandatory.

## 46.5 Runtime Version Policy

Runtime versions must be explicitly declared in the repository.

Do not depend on whatever runtime happens to exist on a developer
machine or cloud builder.

### Backend

Use:

``` text
CPython 3.12.x
```

Python 3.12 is intentionally selected as a conservative, broadly
supported production runtime.

Declare the version through project tooling, for example:

``` text
.python-version
```

The project should remain on the latest compatible Python 3.12 patch
release rather than hard-coding an old vulnerable patch indefinitely.

### Frontend

Use:

``` text
Node.js 24 LTS
```

Declare the major runtime explicitly, for example through:

``` text
.nvmrc
```

and/or the frontend `package.json` engines field.

Do not use the non-LTS Node.js Current line for production without a
specific reason.

### PostgreSQL

Use:

``` text
PostgreSQL 17
```

for the initial project unless the selected managed hosting provider
provides a compelling reason to use PostgreSQL 18.

The important requirement is to use a currently supported PostgreSQL
major version and keep the production major version consistent with
local development.

### pgvector

Use a current stable pgvector release compatible with the selected
PostgreSQL major version.

Pin the Docker image/version used for local development.

Do not use an unversioned `latest` tag.

------------------------------------------------------------------------

# 47. Dependency Management

## 47.1 Python

Use `uv` as the Python project/package manager.

Expected project files:

``` text
pyproject.toml
uv.lock
.python-version
```

The lockfile must be committed to Git.

Typical workflow:

``` bash
uv sync
uv run pytest
uv run ruff check .
```

Application dependencies belong in `pyproject.toml`.

Do not maintain a manually edited `requirements.txt` as the primary
dependency source unless a deployment platform explicitly requires an
exported requirements file.

If an exported file is needed, generate it from the locked project
configuration.

## 47.2 JavaScript / TypeScript

Use `pnpm`.

Expected files:

``` text
package.json
pnpm-lock.yaml
```

Commit `pnpm-lock.yaml`.

CI must install dependencies using the frozen lockfile.

Do not allow CI to silently rewrite dependency versions.

## 47.3 Dependency Update Policy

For the prototype:

-   pin/lock all resolved dependencies
-   use supported major versions
-   avoid unnecessary bleeding-edge libraries
-   review major upgrades intentionally
-   patch security vulnerabilities promptly
-   never use `latest` as a production dependency strategy

------------------------------------------------------------------------

# 48. Python Engineering Standards

## 48.1 Formatting and Linting

Use:

``` text
Ruff
```

for Python linting and formatting.

Expected commands:

``` bash
uv run ruff check .
uv run ruff format --check .
```

Local formatting:

``` bash
uv run ruff format .
```

## 48.2 Type Checking

Use:

``` text
mypy
```

Start with practical strictness and increase it over time.

Domain services, schemas, provider interfaces, AI tools, and repository
interfaces should be strongly typed.

## 48.3 Tests

Use:

``` text
pytest
pytest-asyncio
```

where asynchronous tests are required.

Coverage should focus on business-critical logic rather than chasing an
arbitrary percentage.

High-priority tests include:

-   Household isolation
-   internal transfer exclusion
-   income/expense aggregation
-   duplicate detection
-   approval workflow
-   net worth calculations
-   snapshot history
-   AI tool authorization

## 48.4 Database Access

Use:

``` text
SQLAlchemy 2.x
Alembic
```

Application code must not modify the production schema manually.

Every schema change must be represented by an Alembic migration
committed to Git.

------------------------------------------------------------------------

# 49. Frontend Engineering Standards

Use:

``` text
Next.js
React
TypeScript
Tailwind CSS
shadcn/ui
```

Use TypeScript strict mode.

Recommended frontend quality tools:

``` text
ESLint
Prettier where needed
Vitest
React Testing Library
Playwright
```

Use Playwright for critical end-to-end workflows.

The UI must be responsive from the beginning because the dashboard will
likely be opened from mobile devices even though the initial product is
a web application.

------------------------------------------------------------------------

# 50. Environment Configuration

No environment-specific secrets or credentials may be committed to Git.

Create:

``` text
.env.example
```

It should contain variable names and safe placeholders only.

Example:

``` text
APP_ENV=development
DATABASE_URL=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
LLM_PROVIDER=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
EMBEDDING_PROVIDER=
TELEGRAM_BOT_TOKEN=
OBJECT_STORAGE_ENDPOINT=
OBJECT_STORAGE_BUCKET=
OBJECT_STORAGE_ACCESS_KEY=
OBJECT_STORAGE_SECRET_KEY=
REDIS_URL=
```

Local developers create their own:

``` text
.env
```

`.env` must be ignored by Git.

Production values belong in the cloud provider's secret/environment
management system.

Validate required configuration during application startup and fail
clearly when required values are missing.

------------------------------------------------------------------------

# 51. Local Development Environment

A new developer or coding agent should be able to start the project with
a small number of documented commands.

Recommended local dependencies:

``` text
PostgreSQL + pgvector
Redis, when async queue work begins
S3-compatible local object storage if required
```

Use Docker Compose for infrastructure dependencies.

Application processes may run directly on the developer machine for
faster iteration.

Target developer experience:

``` bash
git clone https://github.com/ruvicohen/financial_managed.git
cd financial_managed

# backend
uv sync

# frontend
pnpm install

# infrastructure
docker compose up -d

# migrations
uv run alembic upgrade head

# run development servers
```

The final README must contain exact working commands rather than
conceptual instructions.

------------------------------------------------------------------------

# 52. Docker Standards

Create production-ready Dockerfiles for deployable services.

At minimum:

``` text
apps/api/Dockerfile
apps/web/Dockerfile
```

and a worker Dockerfile when the asynchronous document worker is
introduced.

Rules:

-   use explicit base-image versions
-   prefer slim production images
-   use multi-stage builds where useful
-   run application processes as a non-root user where practical
-   do not bake secrets into images
-   keep build context small with `.dockerignore`
-   expose health endpoints
-   ensure deterministic dependency installation
-   never use an unversioned `latest` base image

------------------------------------------------------------------------

# 53. CI Pipeline

Use GitHub Actions.

CI should run for:

``` text
pull_request -> main
push -> main
```

Initial CI jobs:

## Backend Quality

``` text
uv sync --locked
ruff check
ruff format --check
mypy
pytest
```

## Frontend Quality

``` text
pnpm install --frozen-lockfile
lint
typecheck
unit tests
build
```

## Migration Validation

CI should verify that migrations can be applied to a clean PostgreSQL
database.

As the project matures, also test upgrade paths from the previous
schema.

## Security / Hygiene

At minimum:

-   verify no obvious secrets are committed
-   dependency/security scanning can be added through GitHub-native
    tooling or another maintained solution

## End-to-End

Once the first vertical slice exists, run Playwright against an
ephemeral or test environment where practical.

------------------------------------------------------------------------

# 54. CD / Production Deployment

Deployment must occur automatically after successful changes reach
`main`.

Conceptual pipeline:

``` text
Feature Branch
    |
Pull Request
    |
GitHub Actions CI
    |
Merge to main
    |
Production Build
    |
Database Migration
    |
Deploy Backend / Worker / Frontend
    |
Health Check
    |
Public HTTPS URL
```

A failed CI pipeline must never trigger production deployment.

A failed production health check must be visible as a deployment
failure.

Database migrations must be run in a controlled step before or during
deployment.

Prefer backward-compatible migrations as the application becomes more
mature.

------------------------------------------------------------------------

# 55. Initial Hosting Layout

The first deployment should optimize for simplicity and low cost.

The intended logical deployment is:

``` text
Public Internet
      |
      v
Web Frontend
      |
      v
FastAPI Backend
      |
      +-------------------+
      |                   |
      v                   v
PostgreSQL            Background Worker
+ pgvector                 |
                           v
                      Object Storage
```

Redis may be added when the background-job implementation requires it.

A managed platform such as Render is the preferred starting point,
subject to a final pricing/capability check at implementation time.

Do not introduce Kubernetes for the prototype.

The production deployment must provide:

-   HTTPS
-   public web URL
-   backend service
-   PostgreSQL
-   persistent document storage
-   background worker capability
-   secret management
-   deploy logs
-   health monitoring

The architecture must remain portable to AWS/GCP/Azure later.

------------------------------------------------------------------------

# 56. Health Checks

Backend endpoints:

``` text
GET /health
GET /ready
```

`/health` verifies that the process is alive.

`/ready` verifies critical dependencies required to serve requests, such
as database connectivity.

Do not expose sensitive dependency details publicly.

The frontend should also expose a platform-compatible health signal
where needed.

------------------------------------------------------------------------

# 57. Database Migration Policy

All database changes use Alembic.

Rules:

1.  Never manually alter production schema as the normal workflow.
2.  Every migration is committed to Git.
3.  Migrations must have descriptive names.
4.  CI verifies migrations on a clean database.
5.  Destructive migrations require explicit review.
6.  Avoid combining unrelated schema changes.
7.  Prefer expand/migrate/contract patterns once production data becomes
    important.

The coding agent must run:

``` bash
uv run alembic upgrade head
```

before considering a schema-dependent task complete.

------------------------------------------------------------------------

# 58. Repository Files Required Early

The repository should quickly converge on the following baseline:

``` text
financial_managed/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── apps/
│   ├── api/
│   │   ├── app/
│   │   ├── tests/
│   │   └── Dockerfile
│   └── web/
│       ├── src/
│       └── Dockerfile
├── workers/
├── packages/
├── infra/
├── docs/
├── .env.example
├── .gitignore
├── .dockerignore
├── .python-version
├── .nvmrc
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── package.json
├── pnpm-lock.yaml
└── README.md
```

Exact workspace layout may evolve, but changes should be intentional.

------------------------------------------------------------------------

# 59. README Requirements

The root README is part of the product engineering deliverable.

It must explain:

-   product purpose
-   architecture summary
-   prerequisites
-   required runtime versions
-   cloning the repository
-   environment setup
-   Google OAuth setup
-   database startup
-   migrations
-   backend startup
-   frontend startup
-   test commands
-   lint/type-check commands
-   Docker usage
-   production deployment overview
-   where architectural documentation lives

The README must stay executable: commands documented there should
actually work.

------------------------------------------------------------------------

# 60. Coding Agent Operating Instructions

When this plan is provided to Claude or another coding agent, it should
follow these rules.

## Before Feature Development

The coding agent must first:

1.  clone/open the canonical repository
2.  inspect existing code before modifying it
3.  initialize the monorepo structure if absent
4.  configure Python 3.12
5.  configure Node.js 24 LTS
6.  configure `uv`
7.  configure `pnpm`
8.  configure PostgreSQL + pgvector locally
9.  configure Docker Compose
10. configure Ruff
11. configure mypy
12. configure pytest
13. configure frontend lint/type checks/tests
14. create `.env.example`
15. configure Alembic
16. configure GitHub Actions CI
17. create production Dockerfiles
18. configure the first cloud deployment
19. expose a public HTTPS application URL
20. verify CI -\> deploy works from `main`

Only after the engineering foundation is functional should substantial
financial features begin.

## For Every Task

Before coding:

-   read this plan
-   inspect relevant existing code
-   identify affected domain boundaries
-   identify required migrations
-   identify required tests

During coding:

-   keep changes scoped
-   reuse domain services
-   maintain Household isolation
-   add/update tests
-   do not bypass review workflows
-   do not add provider-specific business logic unnecessarily

Before marking the task complete:

-   run backend linting
-   run backend type checks
-   run backend tests
-   run frontend checks if affected
-   run migrations if affected
-   verify build
-   update documentation when setup/behavior changed

## Do Not

The coding agent must not:

-   redesign the architecture silently
-   replace core technologies without documenting the reason
-   commit secrets
-   bypass Household authorization
-   let the LLM execute unrestricted SQL
-   let LLM output become authoritative financial data without
    validation/review
-   skip migrations
-   use unpinned production Docker images
-   create unnecessary microservices
-   introduce Kubernetes
-   prematurely optimize for massive scale

If a plan decision becomes technically invalid, the agent should
document the conflict and propose the smallest justified change.

------------------------------------------------------------------------

# 61. Phase 0 Detailed Acceptance Criteria

Phase 0 is complete only when all of the following are true:

-   canonical GitHub repository is initialized
-   `main` exists as the deployment branch
-   backend starts with Python 3.12
-   frontend starts with Node.js 24 LTS
-   dependencies are locked
-   PostgreSQL + pgvector run locally
-   migrations execute successfully
-   `/health` works
-   frontend can call backend in development
-   Ruff passes
-   mypy passes
-   pytest passes
-   frontend lint passes
-   frontend type check passes
-   frontend build passes
-   Docker builds succeed
-   `.env.example` exists
-   secrets are excluded from Git
-   GitHub Actions CI runs on pull requests
-   CI runs on `main`
-   production deployment is connected to `main`
-   production uses HTTPS
-   a public application URL exists
-   a change merged into `main` can reach production without manual
    server deployment

No financial feature implementation should be considered the first
milestone until this foundation is demonstrably working.

------------------------------------------------------------------------

# 62. Technology Decision Summary

The initial implementation baseline is:

``` text
Repository:
  GitHub
  https://github.com/ruvicohen/financial_managed.git

Git:
  main + short-lived feature branches
  pull requests
  Conventional Commits
  protected main with required CI checks where available

Backend:
  CPython 3.12.x
  FastAPI
  Pydantic
  SQLAlchemy 2.x
  Alembic
  uv
  Ruff
  mypy
  pytest

Frontend:
  Node.js 24 LTS
  pnpm
  Next.js
  React
  TypeScript
  Tailwind CSS
  shadcn/ui
  Recharts
  ESLint
  Vitest
  Playwright

Data:
  PostgreSQL 17
  pgvector
  S3-compatible object storage
  Redis only when required by background processing

AI:
  provider-independent LLM interface
  provider-independent embedding interface
  controlled domain tools
  no unrestricted LLM SQL

Infrastructure:
  Docker / Docker Compose
  GitHub Actions
  low-cost managed cloud platform
  Render preferred initially, subject to implementation-time validation
  HTTPS public URL

Deployment:
  merge to main
  CI succeeds
  migration
  deployment
  health verification
```

This technology baseline should be treated as the default implementation
contract for the prototype.
