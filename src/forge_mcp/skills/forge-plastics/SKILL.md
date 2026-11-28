---
name: forge-plastics
description: Optional Forge knowledge for specialized plastic design features such as enclosure lips, cantilever snap-fits, screw bosses and support rests. Not for plastic material or printing alone.
---

# Forge plastic features

Use only when the requested geometry benefits from these specialized Forge
features. Ordinary printed or molded solids use the common `forge-modeling`
route. Do not reread that skill if already loaded.

Choose only the relevant feature and read its installed-release contract:

- `references/api/Lip.json`: enclosure rim lip.
- `references/api/SnapFit.json`: cantilever snap-fit with explicit hook direction.
- `references/api/Boss.json`: cylindrical support/screw boss with optional hole.
- `references/api/Rest.json`: support pad or elongated rest.

These features are added to the design with `+`. If placement is unclear,
read `references/guide/transformations.html` or the specific
`references/api/Shape.attach.json` contract. Respect the supported parent
shapes, face/anchor rules and direction vectors. For shell geometry, consult
`references/guide/features.html` only if needed.

Verify feature placement and requested dimensions with SolidCraft. Material
choice, printable clearance and mechanical fit are design requirements;
a successful geometry build alone does not prove strength or fit.
