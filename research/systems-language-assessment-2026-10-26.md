# Systems-language assessment for PayPal AI Hackathon

Decision: use a familiar Python/TypeScript product stack with at most one additional systems-language core, provisionally Rust. Select the core for a demonstrable property such as portable deterministic checking, bounded execution or reproducible fault analysis. No implementation or benchmark was performed in this assessment. No PDFs were generated or changed.

## Evidence corrections

- The Go case study is dated June 1, 2020. It documents a NoSQL rewrite and build/test infrastructure. It cannot establish PayPal's current company-wide language distribution: https://go.dev/solutions/paypal
- PayPal's 2016 squbs post documents Scala/Akka engineering, beyond a claim that Scala only exists in batch analytics: https://medium.com/paypal-tech/squbs-a-new-reactive-way-for-paypal-to-build-applications-127126bf684b
- A 2024 PayPal Spark post discusses updating Scala compilation during migration: https://medium.com/paypal-tech/leveraging-spark-3-and-nvidias-gpus-to-reduce-cloud-cost-by-up-to-70-for-big-data-pipelines-e0bc02ec4f88
- The focused primary-source search did not establish increasing internal Rust adoption. Community PayPal Rust clients establish client availability, not internal adoption. Failure to find public evidence also does not establish non-use.
- No evidence supports the pasted claim that 90% of competing submissions use the same stack. Registration count is not the number of eligible competing projects. No win-probability model is supported by the available evidence.
- Official rules weight implementation, design, impact, innovation and presentation equally. Language rarity has no separate stated criterion: https://paypalaihackathon.devpost.com/rules

## Candidate systems components

### Assembly: independently checkable configuration and purchase record

Python handles model calls, retrieval and candidate search. A strict typed intermediate representation records requirements, product variants, quantities, ports, capacities, evidence timestamps, unresolved facts and exact merchant offer. A small Rust checker, authored independently from the candidate search, verifies a proposed selection against those recorded facts and rules. It returns satisfied constraints, conflicts and unknowns. Use a bounded category-specific search before adopting a larger solver.

The same checker crate can expose a browser WebAssembly interface for immediate feedback and a native server interface for authoritative verification. Both receive the same versioned input contract. Browser validation is advisory. Server authorization, accepted configuration version and current offer must be rechecked before payment. Shared code reduces divergence between surfaces; independent search/checking reduces trust in the planner.

The decision record binds the selected configuration, rule/evidence versions, merchant, total, currency and authenticated approval. A hash detects changes to recorded bytes. It does not prove specifications truthful, authenticate a user by itself, or replace current authorization. Deterministic checking requires controlled iteration, exact arithmetic and explicit external inputs.

Best demonstration: a four-microphone configuration fails a two-input interface rule; a replacement passes; changing a critical specification invalidates the accepted decision; the updated version receives approval and a genuine PayPal sandbox capture. Demonstrate a rejected altered record, not just a displayed hash.

### PayGuard: payment authority kernel

Rust can provide strict request types, pure policy evaluation and explicit lifecycle transitions. It does not provide business correctness or cross-process transaction atomicity merely by compilation. Persistent uniqueness, transactional checks and application-level reconciliation remain necessary. Keep payment credentials outside the model and untrusted code. Revalidate the exact current offer and authority before a side effect.

Best demonstration: concurrent attempts cannot consume the same one-time approval twice; a changed offer invalidates approval; a lost capture response creates an unknown outcome which is reconciled using the recorded provider operation rather than creating an independent new purchase. Provider idempotency is endpoint- and retention-dependent; do not claim globally exactly-once payment effects.

### Checkout Wind Tunnel: deterministic fault runner

A Rust or Go discrete-event runner can inject faults into our own application, control a test clock and scheduler, replay seeded scenarios, check independently authored invariants and shorten failure traces. AI proposes cases and explanations. It does not define the sole correctness oracle. Real PayPal calls belong in labelled integration runs; deterministic local replay does not deterministically control PayPal's network or internal state.

Undermind metadata/abstracts support investigating deterministic simulation and history analysis. Full texts were unavailable in that tool for this read. FoundationDB: https://doi.org/10.1145/3448016.3457559 ; Elle: https://doi.org/10.1145/3465084.3467483

## Language choices and limits

- Rust: best provisional fit for a small portable checker, strict domain types or native runner. Memory safety does not prevent duplicate business orders or incorrect authority checks. https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html
- Go: strong alternative for an executor, webhook service or fault runner when deployment simplicity and team familiarity dominate.
- Elixir/Erlang: consider as the primary workflow runtime when supervision and many concurrent live sessions are central. Restarting a process does not roll back a payment or durably restore its mailbox. https://www.erlang.org/doc/system/design_principles.html
- OCaml: useful for an intent DSL, parser, type checker or symbolic transformation when the team already knows it. Avoid implementing a separate compiler solely for rarity.
- Zig: useful for a demonstrated allocation-sensitive parser, native library or low-level boundary. No measured need has been established for these projects. https://ziglang.org/documentation/master/
- Scala/Java: consider for JVM integration or an actual stream-processing workload; no current requirement justifies a Spark/Kafka deployment for the prototype.
- C++: justified by existing expertise or required libraries, rather than a general promise of speed.

Wasmtime can bound execution with fuel; its docs describe deterministic interruption conditional on other nondeterminism and additional overhead versus epochs. Resource isolation requires careful allowed host functions, memory limits and host-call timeouts as well. https://docs.wasmtime.dev/examples-interrupting-wasm.html

## Selection gate

Compare a familiar-stack baseline and the proposed systems component on identical inputs. Report correctness separately from p50/p95 latency, memory, startup and integration complexity. For fault recovery, measure business duplicates, time to reconcile and reproducibility under recorded injected faults. For Assembly, measure held-out rule violations, unknown handling, altered-record rejection and client/server parity. Any claim must specify machine, workload and sample size.

Illustrative arithmetic, not a measurement: 3,000 ms of external work plus 5 ms local validation gives 3,005 ms total. Reducing local validation to 0.5 ms saves 4.5 ms, about 0.15%. Local speed must be material to the product before it justifies a rewrite.

All ten sponsors remain the user's stated product requirement. That integration burden strengthens the case for a single additional runtime. Prototype the systems property in a tightly bounded spike; retain it only if the demonstration and engineering benefit justify the integration cost.
