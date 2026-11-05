# Assembly Proof architecture pack

Two reference architectures, dated November 1, 2026. The diagrams describe a proposed system; they are not a deployed application, an audit certificate or a performance benchmark.

- Start with [ARCHITECTURES.md](ARCHITECTURES.md) for design decisions, data contracts, CAP choices, security controls, capacity arithmetic, all ten sponsor roles and research sources.
- Open [DIAGRAMS.md](DIAGRAMS.md) for all 14 diagrams.
- `diagrams/` contains vector SVGs for zooming and PNG previews.
- `source/` contains editable Graphviz DOT and alternative Mermaid flow sources.
- `diagram-manifest.json` describes the render inventory.
- `capacity-scenarios.json` records illustrative throughput arithmetic, not measured capacity.
- `verification.json` and `SHA256SUMS.txt` record artifact checks.

Architecture A contains six views: single-region deployment, purchase flow, capture state, data model, security boundaries and independent tests. Architecture B contains six views: regional cells, consistency/ownership, surge control, failover, funds/reconciliation and regional security. Two shared views map sponsor ownership and business-value measurement.

To rerender one editable DOT source with Graphviz installed:

```sh
dot -Tsvg source/A1-deployment.dot -o diagrams/A1-deployment.svg
dot -Tpng source/A1-deployment.dot -o diagrams/A1-deployment.png
```

Graphviz was the verified rendering path. Mermaid sources describe the same nodes and relationships as flowcharts but omit Graphviz cluster styling. Their rendering was not independently exercised.

Use Architecture A for the current build. Architecture B requires additional operational engineering, database compatibility work, account/region validation, representative testing and commercial decisions. The application manages purchase authority and provider records; it does not hold customer deposits.
