---
name: forge-modeling
description: Use when building a new maintainable Python Forge CAD model from an empty or newly scaffolded scpf/model.py.
---

# Forge modeling

Use this skill when creating a new Forge model. The maintained design is Python source in `scpf/model.py`; generated SolidCraft command JSON is build output, not source.

## Before the first write

1. Call `workspace_status` and stay inside the configured workbench/owner.
2. Read this skill before authoring.
3. Read `references/cheatsheet.yml` and `references/api.md`. Use `references/api/<Symbol or Symbol.method>.json` for exact current signatures.
4. Use `references/index.json` only when you need a guide or a nearby qualified example. Read the selected example through `skill_reference`; do not inspect the Forge checkout directly.
5. Write down the model parameters, origin/placement intent and expected result before adding geometry.

## Starting a new `scpf/model.py`

A new root model has four parts:

1. import the public Forge/SCPF names it uses;
2. define one public model class;
3. put editable numeric dimensions on the class as lower-case fields;
4. return the root Shape/assembly from `build()`, then instantiate the root model once.

Smallest useful model:

```python
from scpf import Anchor, Box


class Plate:
    length = 60.0
    width = 20.0
    thickness = 4.0

    def build(self):
        return Box(
            self.length,
            self.width,
            self.thickness,
            anchor=Anchor.BOTTOM,
        )


Plate()
```

No `main()`, `show()` or handwritten SolidCraft command JSON is required.

Forge's runner also makes the public SCPF modeling symbols available while executing a model, so older qualified examples may omit the explicit `from scpf import ...` line. For new standalone source, explicit imports are preferred because the maintained Python file is self-describing.

### Parameter rules

- lower-case numeric class fields such as `length = 60.0` become editable native model parameters;
- lower-case fields beginning with `_` are Forge/build-time inputs and are not published as native model parameters;
- `UPPER_CASE` numeric fields are fixed class constants;
- `@dataclass` is optional; a plain class is sufficient for the normal root model.

Keep symbolic relationships symbolic. Do not turn a parameter into a concrete Python number just to make a feature work.

### Adding a centred through-hole

Prefer the highest-level qualified feature that expresses the design intent. A centred through-hole in a plate can start as:

```python
from scpf import Anchor, Box, Depth, Faces, Hole


class Plate:
    length = 60.0
    width = 20.0
    thickness = 4.0
    hole_d = 8.0

    def build(self):
        plate = Box(
            self.length,
            self.width,
            self.thickness,
            anchor=Anchor.BOTTOM,
        )
        hole = Hole(
            d=self.hole_d,
            depth=Depth.THROUGH_ALL,
        ).on(plate, face=Faces.TOP)
        return plate - hole


Plate()
```

Use an explicit `Sketch` when the design itself contains authored 2D profile intent or when the needed feature is not represented by a qualified high-level Forge feature. For sketch/profile/extrude work, read the exact API signatures and a nearby qualified example before writing the source; do not guess coordinate or anchor semantics.

## Build and verify

1. Write `scpf/model.py` with `workspace_write`.
2. For interactive work, read the `solidcraft-control` skill and use `forge_live` to compile/apply the maintained source to the running SolidCraft GUI.
3. Inspect the active design with `solidcraft_live_inspect`.
4. Verify dimensions/parameters/structure, then use a semantic SolidCraft parameter edit when the acceptance requires mutation.
5. Inspect again, set a useful view and retrieve image evidence with `solidcraft_live_render`.
6. Use `forge_compile` plus headless SolidCraft replay/evaluate/snapshot when independent saved evidence is required.
7. Correct design intent in the Python source rather than leaving accidental GUI-only geometry edits as the maintained result.

Use both numeric/structural and visual evidence before claiming success. A successful tool reply or image alone is not enough.

## Reuse and assemblies

Keep component definitions separate from occurrences. Use Forge's documented placement, support and attachment semantics; do not invent API methods.

The configured model root is authoritative and the only writable owner. Never search the surrounding CAD library for a different target model or switch model roots implicitly. If the configured owner is wrong or missing, stop and report the configuration problem.

Assemblies and subassemblies may depend on other owners in the same configured CAD library. Use `catalog_dependency_list(owner)` and `catalog_dependency_read(owner, path)` only for an exact dependency owner/path already named by the target source, metadata, imports or the user. Dependency access is read-only and must never replace target selection.

If converting an existing native SolidCraft design instead of starting a new Forge model, use the `solidcraft-to-forge` skill.
