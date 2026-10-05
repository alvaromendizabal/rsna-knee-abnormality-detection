# System architecture

## Overview

This project is organized as a **research system**, not a single model. The scored parent combines heterogeneous image-model families, fitted numerical aggregation, strict input identity, and an experiment-control layer that governs validation, cost, resumability, and promotion.

```mermaid
flowchart TB
    subgraph DATA["Data + identity"]
        A1[MRI / DICOM]
        A2[Series metadata]
        A3[Labels + lineage]
        A4[Input signatures]
    end

    subgraph AWS["AWS / SageMaker canonical research state"]
        B1[Canonical cache]
        B2[Experiment runner]
        B3[Private S3 artifacts]
        B4[Telemetry + cost ledger]
        B5[Immutable manifests]
    end

    subgraph PARENT["Heterogeneous parent"]
        C1[Native DINO<br/>20 trained members]
        C2[RadImageNet family<br/>3 layouts]
        C3[A5<br/>5 folds]
        C4[Raptor<br/>4 diagnostic views]
        C5[CoAt families<br/>7 trained predictions]
        C6[Fixed numerical<br/>calibration + fusion]
    end

    subgraph RESEARCH["Controlled research additions"]
        D1[Global-only residual control]
        D2[Anatomical regional pooling]
        D3[Visibility-aware auxiliary task]
        D4[Multiple localization proposals]
    end

    subgraph GOVERNANCE["Scientific + engineering governance"]
        E1[Grouped validation]
        E2[Leakage / lineage audit]
        E3[Numerical parity]
        E4[Resume + regression tests]
        E5[Champion / challenger registry]
    end

    A1 --> B1
    A2 --> B1
    A3 --> E1
    A3 --> E2
    A4 --> B2

    B1 --> C1
    B1 --> C2
    B1 --> C3
    B1 --> C4
    B1 --> C5

    C1 --> C6
    C2 --> C6
    C3 --> C6
    C4 --> C6
    C5 --> C6

    C6 --> E1
    C6 --> E3
    E1 --> E5
    E2 --> E5
    E3 --> E5

    B2 --> B3
    B2 --> B4
    B2 --> B5
    E4 -. governs .-> B2

    B1 --> D1
    B1 --> D2
    D2 --> D3
    D3 --> D4
    D1 --> E1
    D2 --> E1
    D3 --> E1
    D4 --> E1
```

## Design principle: model identity includes data identity

A checkpoint alone is not treated as the model.

The effective model identity includes:

- checkpoint/source state;
- selected series and slices;
- image transforms;
- target order;
- fitted aggregation/calibration;
- evaluation membership.

When newly recovered acquisitions change selected pixels, only affected branches are invalidated. Unaffected outputs remain reusable.

## Parent component status

| Component | Public-safe status | Why it matters |
|---|---|---|
| Native DINO | 20 trained members / 200 member-window evaluations | Strong heterogeneous image representation |
| RadImageNet family | 3 source layouts / multiple trained heads | Medical-pretraining diversity |
| A5 | 5/5 trained folds | Complementary learned branch |
| Raptor | 4/4 diagnostic views on partial input scope | Additional spatial/model diversity |
| CoAt families | 8/8 gates + 7/7 trained predictions | Recovered spatial/depth aggregation families |
| Numerical graph | Fixed fitted calibration/fusion preserved | Prevents accidental retraining during restoration |

Full historical parity is deliberately not claimed while complete compatible acquisitions and independent evaluation membership remain unresolved.

## Control plane

The research control plane is as important as the model graph.

### Before execution
- verify artifact/source identity;
- discover hardware and disk headroom;
- run deterministic self-tests;
- validate metric/evaluation contract;
- benchmark representative worker/batch choices when needed.

### During execution
- emit timestamped heartbeats;
- track completed/total/remaining work;
- record process/system/GPU memory;
- preserve current and peak utilization;
- accumulate estimated compute cost;
- checkpoint independently reusable units.

### After execution
- validate outputs;
- compare numerical parity where relevant;
- write immutable manifests;
- update the experiment registry;
- produce one compact return bundle;
- preserve nonzero failure status if the run failed.

## Failure recovery

```mermaid
flowchart LR
    A[Start / resume] --> B{Completed artifact valid?}
    B -- yes --> C[Reuse]
    B -- no --> D[Execute missing unit]
    D --> E{Gate passes?}
    E -- yes --> F[Commit immutable artifact]
    E -- no --> G[Package diagnostics + stop]
    F --> H{More units?}
    H -- yes --> B
    H -- no --> I[Validate final result]
    I --> J[Notebook + manifest + registry]
```

This design prevents a late failure from forcing expensive earlier stages to rerun.

## Validation architecture

The project separates four evidence classes:

1. **External recorded performance** — comparable public result.
2. **Grouped internal development evidence** — model-selection research.
3. **Engineering parity** — source/runtime equivalence checks.
4. **Exploratory analysis** — useful but not independent confirmation.

They are intentionally not collapsed into one score.

## Anatomy-aware extension

The current research program adds a new capability without replacing the parent.

```mermaid
flowchart LR
    A[Parent global features] --> B[Matched global residual]
    A --> C[Anatomy localizer]
    C --> D[ROI + visibility features]
    D --> E[Localized residual]
    B --> F[Controlled comparison]
    E --> F
    F --> G{Localization adds value?}
    G -- no --> H[Keep parent / close route]
    G -- yes --> I[Advance to auxiliary visibility + proposal tests]
```

Missing or low-confidence anatomical evidence must fall back exactly to the parent.

## Public/private architecture boundary

**Public GitHub:** aggregate metrics, diagrams, experiment contracts, public-safe helpers, tests, CI, executed aggregate notebooks.

**Private AWS/S3:** raw MRI, identifiers, row-level predictions, checkpoints, private runners, source handles, exact competition fusion logic, resumable heavy artifacts.

This split makes the repository reviewable and partially reproducible without leaking restricted data or competitive implementation.
