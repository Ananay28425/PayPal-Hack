# Five sponsor tools

| Sponsor | Job and why it matters | Evidence and status |
|---|---|---|
| AG Grid | Sort checked repair candidates by total and select one to inspect its blocker. This explains why the $700 kit fails even though it is cheaper than the $810 repair. | **Exercised locally.** Community grid renders all three computed candidates and row selection reveals the exact rule. Open **Compare checked alternatives** after a repair search. |
| APIMatic | The PayPal Context Plugin's resilience and testing guidance informed a review of ambiguous provider responses. An HTTP 408 now enters reconciliation, and a transport test asserts that exactly one capture POST carries the stored request ID. | **Used in development.** Review the [v0.4.1 context](https://context.apimatic.io/plugins/paypal/), the Python [resilience](https://github.com/context-plugins/plugin-marketplace/blob/main/plugins/paypal/skills/python/python-configuration-resilience/SKILL.md) and [testing](https://github.com/context-plugins/plugin-marketplace/blob/main/plugins/paypal/skills/python/python-testing/SKILL.md) references, and [the regression](tests/test_paypal.py). |
| Bryntum | Show when the repaired kit can actually be used. One delivery or setup dependency should make a kit miss the buyer's required date and visibly change the readiness result. | Scheduler trial rendered locally. The advisory timeline compares delivery plus one setup day with the recording date. |
| Channel3 | Discover the exact product variant and retain its identity through candidate selection. A visually similar model can have a different input count. | Discovery wired. API key, live result, and merchant offer mapping pending. |
| Postman | Exercise the checkout contract from incompatibility through replay. This gives judges a repeatable test of the behavior behind the video. | **Exercised locally.** Newman ran 12 requests and passed 12 assertions in mock mode, including a stale proof, approval mismatch, pre-approval capture, and replay of the same capture ID. |
|---|---|
| Sponsor | Missing components | Acceptance run |
|---|---|---|

## Judge walkthrough

1. Run a Channel3 search with CHANNEL3_API_KEY set on the server. Inspect the exact variant ID. Reference listings remain separate from the synthetic merchant catalogue and payable offers.
2. Run the repair and compare candidates in AG Grid. Select the cheaper failed row to inspect its blocking rule.
3. In Bryntum, enter delivery and recording dates and inspect the setup buffer. The timeline is advisory. Install the optional Scheduler trial with `npm install --no-save --package-lock=false --ignore-scripts @bryntum/scheduler-trial@7.3.8`. Activate the trial if required.
4. Review the APIMatic context links above and the timeout regression. The original PayPal order is reconciled after uncertainty.
5. Run the Postman collection against mock checkout. CI checks consent, stale terms, and capture replay.

## Infrastructure boundary

Discovery can fail independently of checkout. The planner and checker produce reviewable options. Only the server can create and capture the frozen PayPal Sandbox order. Shared PostgreSQL and the reconciliation worker support multiple web instances. Grid and Scheduler run in the browser. APIMatic and Postman help verify the integration without adding payment runtime dependencies. Live Channel3 and Sandbox verification require credentials. Global production capacity has not been measured.
