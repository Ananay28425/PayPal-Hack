# Assembly Proof visual system

Inspected on 5 November 2026:

- [Builders Table](https://builderstable.net/?ref=onepagelove) and its [hackathon page](https://builderstable.net/hackathon) for the visual composition.
- PayPal's [2025 Merchant Partner Toolkit](https://www.paypalobjects.com/paypal-world/media/us-merchant-toolkit-v4.pdf) and [Brand Identity Quick Guide](https://filecache.mediaroom.com/mr5mr_paypal/184713/download/PP_Brand%20Guidelines_Newsroom_2022.pdf) for published palette values.

The reference site is an event website. Assembly Proof keeps its product-specific content and uses a warm light interface after user review. Abstract illustrations and the hero collage were removed because they did not explain the purchase workflow.

## What was observed

| Reference pattern | Assembly Proof implementation |
| --- | --- |
| Large, light-weight uppercase editorial headline | Two-line commerce statement on a warm white canvas |
| Fluorescent primary action and thin outlined secondary action | PayPal gold primary action and outlined secondary action |
| Small mono labels, section numbers, and thin rules | Indexed rails and panel metadata throughout the page |
| Clear section changes | Warm white, soft neutral, and light blue surfaces |
| Sharp controls | Square panels, dividers, and readable status text |

## PayPal palette used

- Dark text and button ink: `#001435` (published slate in PayPal's earlier brand guide).
- Deep blue: `#002991` (published in the 2025 Merchant Partner Toolkit).
- Action blue: `#0070e0` (published PayPal blue).
- Bright blue: `#60cdff` (published in the 2025 toolkit).
- Gold: `#ffd140` (published PayPal gold, used sparingly for primary action and emphasis).
- Serenity surface: `#e5f0fa` (published light blue).

The implementation uses these as interface colors, without presenting Assembly Proof as an official PayPal product or inventing a PayPal logo treatment.

## Product hierarchy

1. **Hero:** “AI builds the cart. You own the decision.” The copy names planning, independent checking, explicit approval, and PayPal execution.
2. **System:** short text explains the purchasing problem and links to the demo.
3. **Working demo:** goal, bounded AI catalogue proposal, editable kit, and deterministic check.
4. **Proof:** the result shows specific pass/fail/unknown checks and repair guidance.
5. **Payment:** frozen terms, user approval, mock or sandbox buyer step, verified capture, and audit events.
6. **Counterexample lab:** independently specified fixture outcomes remain visible.

## Behavior and limits

- Mobile stacks every section in reading order. The catalogue uses normal page scrolling.
- Inputs have labels, keyboard focus remains visible, status is conveyed with text as well as color, and reduced-motion preferences disable smooth scrolling.
- The AI planning button is disabled when `OPENAI_API_KEY` is absent. Manual presets remain usable. Mock checkout is explicitly identified as a simulation.
- Visual resemblance is purposeful; pixel-identical replication would require the reference site's proprietary typography, assets, and unrelated event content, which this project does not use.
