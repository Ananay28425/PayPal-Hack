# Sponsor integration and sources — revision 2

Status: documented capabilities and proposed roles, 2026-10-23. No actual sponsor integration is claimed. All ten are required by the user; each has a distinct place in the proposed product or its engineering toolchain.

| Sponsor | Documented capability | Proposed Assembly role | Boundary | Access |
|---|---|---|---|---|
| [AG Grid](https://paypalaihackathon.devpost.com/details/aggrid) | AG Studio supports embedded grids, charts, custom widgets and an agent framework. | Configuration comparisons and source-linked conflict widgets. | The UI must display backend-checked results, not create payment authority. | 45-day trial advertised. |
| [APIMatic](https://paypalaihackathon.devpost.com/details/apimatic) | The PayPal Context Plugin supplies API/SDK context to coding tools. | Build the PayPal adapter and record a concrete context-assisted integration example. | Development assistance; not a runtime payment validator. | PayPal plugin needs no separate APIMatic credentials; subscription offers have conditions. |
| [Astropods](https://paypalaihackathon.devpost.com/details/astropods) | Deployable agent blueprints, tool integrations and observability; container HTTP/FastAPI is documented. | Host the requirement/specification compiler with traces. | Authenticated invocation and account resource/model limits need a live spike. | Free account advertised; operational limits unverified. |
| [Bryntum](https://paypalaihackathon.devpost.com/details/bryntum) | Gantt dependencies and resource Scheduler/Calendar components. | Editable delivery, assembly and setup dependencies. | Backend domain logic remains authoritative for feasibility. | 45-day trial advertised. |
| [Channel3](https://paypalaihackathon.devpost.com/details/channel3) | Product discovery and enrichment with prices, offers, variants and retailer links. | Find candidates and connect evidence to exact variants. | No implied retailer payment authority; missing technical specifications stay unknown. | 20,000 hackathon API credits advertised. |
| [Elastic](https://paypalaihackathon.devpost.com/details/elastic) | Structured, text and vector search, including hybrid retrieval. | Retrieve normalized specifications and original evidence passages. | Search projections do not replace durable order state. | 14-day cloud trial, further 30-day extension path; local option documented. |
| [Kernel](https://paypalaihackathon.devpost.com/details/kernel) | Cloud browser sessions with live views and video recordings. | Inspect permitted specification pages and retain evidence. | Recorded video is not deterministic transaction replay or proof that a claim is true. | $50 hackathon credits advertised. |
| [Postman](https://paypalaihackathon.devpost.com/details/postman) | API design, testing, documentation and monitoring; PayPal collections are available. | Export a configuration-linked payment lifecycle/regression collection. | Use independent assertions; redact tokens and private data. | Free starting plan; selected feature limits need checking. |
| [Render](https://paypalaihackathon.devpost.com/details/render) | Web services, databases, workers and Python/TypeScript workflow tasks. | Run domain/payment API, PostgreSQL and verification jobs. | Automatic retries still require durable operation IDs and application idempotency. | $50 hackathon credits advertised. |
| [Zapier](https://paypalaihackathon.devpost.com/details/zapier) | MCP actions across connected applications with managed connections. | Create an approved setup task after verified capture. | Scope credentials and handle ambiguous action outcomes; do not grant arbitrary AI writes. | 14-day Professional trial then Free; required action availability needs checking. |

Additional primary references:

- [Hackathon rules](https://paypalaihackathon.devpost.com/rules) — Deadline, judging dates, criteria, functional demo, open-source repository and third-party license requirements.
- [Hackathon resources](https://paypalaihackathon.devpost.com/resources) — Official links to all ten sponsors and PayPal developer resources.
- [Channel3 response schema](https://docs.trychannel3.com/guides/response-overview) — Discovery fields and the possibility of absent descriptions, dimensions or variants; product metadata is not a compatibility guarantee.
- [Channel3 product details](https://docs.trychannel3.com/api-reference/v1/product-detail) — Variant/offer structure and country/currency options; access and actual category coverage were not exercised.
- [APIMatic PayPal plugin](https://context.apimatic.io/plugins/paypal.md) — PayPal development context, supported assistants including Codex, and setup instructions.
- [Astropods custom HTTP/FastAPI](https://docs.astropods.com/frontend-agents.md) — Container HTTP deployment and OIDC protection; no anonymous service-to-service access is assumed.
- [AG Studio custom widgets](https://www.ag-grid.com/studio/react/custom-widgets/) — Application-defined widgets can be integrated into AG Studio.
- [Render Workflows](https://render.com/docs/workflows) — Python/TypeScript tasks, managed execution and retries; these do not provide business-level exactly-once payments.
- [Kernel browser observation](https://github.com/kernel/docs/blob/main/introduction/observe.mdx) — Live view and MP4 recordings; deterministic application replay must be implemented separately.
- [PayPal idempotency](https://developer.paypal.com/reference/guidelines/idempotency/) — Request IDs are endpoint-dependent and retained for a bounded time; ambiguous calls require careful reconciliation.
- [PayPal webhooks](https://developer.paypal.com/api/rest/webhooks/rest/) — Retry behavior, verification requirements and simulator limitations.
- [PayPal Orders authorization](https://developer.paypal.com/api/orders/v2/orders-authorize) — Authorize an order following buyer approval; separate authorization from capture.
- [PayPal partner authorization guide](https://developer.paypal.com/platforms/checkout/standard/customize/auth-capture) — Search excerpt includes partner prerequisites and time-limited authorization; not interchangeable with ordinary single-merchant onboarding.
- [Neuro-symbolic AI for Industrial Configuration](https://arxiv.org/abs/2609.29947) — Undermind metadata/abstract reviewed; not full-text validated or reproduced.
- [Ontology-Mediated Neurosymbolic Constraint Acquisition from Multiple Stakeholders](https://arxiv.org/abs/2609.29876) — Undermind metadata/abstract reviewed; not full-text validated or reproduced.
- [Automating End-to-End Test Suite Design for Microservices with Large Language Models](https://doi.org/10.1109/COMPSAC69091.2026.00248) — Undermind metadata/abstract reviewed; not full-text validated or reproduced.

The official rules govern eligibility and judging. Sponsor pages document offers, not actual account access or licensing approval. Project novelty, commercial demand, performance and cost are unmeasured. Candidate names are working labels and have not been cleared for branding.

