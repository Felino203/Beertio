# Project Context — Beertio (POC)

## 1. Project Summary

**Beertio** is a Garmin Connect IQ **widget** that converts **daily calories burned** into a fun visual equivalent of beer units.
It is a **personal learning project** — the author's first Garmin/embedded watch development experience — that will also be **published publicly** on the Connect IQ store.

This dual goal has direct implications for code quality: the codebase must be **clean, readable, and a genuinely good example** of Monkey C development, not just something that works.

**Active phase:** Phase 1 — single-item (Beer) POC.

---

## 2. Author Background & Learning Goals

- **Stack:** React/TypeScript + .NET (C#) fullstack developer. Familiar with C and C++.
- **New to:** Monkey C, Garmin Connect IQ APIs, watch/embedded UI development.
- **Learning goals:** Understand the Connect IQ application lifecycle, Monkey C idioms, on-device rendering, the simulator workflow, and how to ship a real product to the Garmin store.

> **For AI agents:** The author picks up new languages quickly (C-family syntax is familiar). Do not over-explain basic programming concepts. Do explain Monkey C-specific quirks, Connect IQ lifecycle hooks, and API limitations — these are genuinely new territory.

---

## 3. Architecture & Design Principles

The codebase must follow **SOLID** and **DRY** principles and maintain a **clear separation of responsibilities**. Monkey C is object-oriented (class-based, single inheritance) and supports this well.

### Layer structure

| Layer        | Responsibility                                   | Example                                  |
| ------------ | ------------------------------------------------ | ---------------------------------------- |
| **App**      | Entry point, lifecycle, wiring                   | `BeertioApp.mc`                          |
| **Model**    | Data, computation, food item definitions         | `CalorieModel.mc`, `FoodItem.mc`         |
| **View**     | Rendering only — reads from model, never mutates | `BeertioGlanceView.mc`, `BeertioView.mc` |
| **Renderer** | Icon drawing logic (generic, data-driven)        | `FoodIconRenderer.mc`                    |
| **Settings** | Reading and exposing app properties              | `AppSettings.mc`                         |

### Naming convention

- **App-level classes** keep the `Beertio` brand for now (`BeertioApp`, `BeertioView`, `BeertioGlanceView`). These will be renamed in Phase 4 when the project becomes Foodtio.
- **Domain classes** use generic names from day one (`FoodItem`, `FoodIconRenderer`, `CalorieModel`). No beer-specific naming in the model or renderer layers — these will support multiple food items without renaming.

### Key rules

- No magic numbers. All constants live in a dedicated constants file or as named class-level variables.
- Views must not contain business logic. The formula `units = calories / caloriesPerItem` belongs in the model.
- The active food item must be **read from a centralized source** (see §6), never referenced directly as a string or literal in view/rendering code.
- Functions must be small and focused. If a function needs a comment to explain what it does, it should be renamed or split.

---

## 4. Technical Constraints

### Target

- **App type:** Widget (`widget`).
- **Target API Level:** 5.2.0 — matches primary device (FR165).
- **SDK:** Connect IQ SDK 9.1.0 (latest toolchain, compiler, simulator). SDK version and API level are independent.
- **Primary test device:** Garmin Forerunner 165 (API 5.2).

### Widget behavior

- **Glance:** Compact preview shown in the widget glance list. Minimal rendering (icon + number). Displayed before the user taps into the full widget.
- **Widget view:** Opened by selecting the glance. Full-screen rendering with icon + calorie unit count.
- **Live updates** while the widget is visible (timer-based temporal events).
- **No user interaction** in Phase 1 — display only, no tap/swipe handling.

### Monkey C language notes (for a C#/TypeScript developer)

- Dynamically typed by default; optional type annotations supported. Prefer typed declarations for readability.
- No generics. Collections are untyped.
- `null` is valid everywhere — guard at data boundaries.
- Memory constrained — avoid allocations in render loops.
- All code is synchronous.

### Key rendering constraints

- No SVG runtime. Vector icons must be pre-converted to polygon coordinate arrays.
- All layout values derived from `dc.getWidth()` / `dc.getHeight()` at runtime — never hardcoded pixel values.
- Assume **dark background** for color rendering.

### Device compatibility

- Device list maintained manually in `manifest.xml`.
- Screen dimensions vary per device; layout must be fully relative.

---

## 5. What the User Sees

### Glance view (widget list preview)

A compact preview in the widget glance list: **food icon + numeric value** (e.g., `[BeerIcon] 2.7`)

### Widget view (full screen)

Full-screen display showing: **food icon + calorie unit count** (e.g., `[BeerIcon] 2.7`)

### Design philosophy

- Clean, minimal, fun.
- The icon is the main visual identity.
- Instantly understandable at a glance.
- Exact layout, spacing, and sizing are TBD — will be iterated visually.

### Future UI exploration (not Phase 1)

- Scrolling food item icons or richer animations.
- Additional stats or breakdowns.

---

## 6. Food Item Abstraction

Although Phase 1 supports only Beer, the architecture must make it trivial to add new food items later **without modifying view or rendering code**.

### `FoodItem` model

Each food item has:

- A unique ID (e.g., `"beer"`)
- A display name (e.g., `"Beer"`)
- A calories-per-unit value (e.g., `150`)
- Polygon data for the icon renderer

### Item registry

A single file defines all available items. The active item is resolved from this registry based on the current setting — not scattered across the codebase.

### Settings integration

- In Phase 1, the selected item is hardcoded to `"beer"` in code (no user-facing setting).
- Adding a real selector in Phase 3 requires only: exposing the property in settings UI and removing the hardcode. No architectural change.

---

## 7. Vector Graphics Pipeline

### Concept

Source icons are authored as **SVG files** stored in the repo. A **conversion script** (Python) transforms each SVG into a Monkey C polygon array. The SVGs are not shipped in the final app package.

### Icon format

- Multi-color, multi-polygon.
- Each polygon has a color and an array of normalized coordinates (0.0 to 1.0).
- At render time, the `FoodIconRenderer` scales coordinates to actual pixel dimensions.

### Key design choice: single generic renderer

There is **one renderer class** (`FoodIconRenderer`) that draws any icon from polygon data. It is not subclassed per food item — the icon is purely data-driven.

Adding a new food item means: add the SVG, run the conversion script, register the generated data. **No renderer code changes.**

### File locations

```
/tools/convert_icon.py           — conversion script
/tools/icons/beer.svg            — source SVG (not in final package)
/source/icons/BeerIconData.mc    — generated polygon data
/source/renderers/FoodIconRenderer.mc — single generic renderer
```

---

## 8. Settings Architecture

Settings are wrapped by an `AppSettings` class that provides typed access. No other code should read properties directly.

### Phase 1 properties

| Key            | Type   | Default  | Note                          |
| -------------- | ------ | -------- | ----------------------------- |
| `selectedItem` | String | `"beer"` | Hardcoded — no UI exposed yet |

---

## 9. Development Workflow

```
Edit in VS Code  -->  Build (Monkey C extension)  -->  Simulate  -->  Iterate
```

- **VS Code** with official Monkey C extension.
- **Garmin Connect IQ SDK 9.1.0** — compiler, simulator, device images.
- **Python 3** — SVG-to-Monkey C icon conversion.
- Project scaffolded via the **Monkey C VS Code extension** (standard project generator).

---

## 10. Roadmap

### Phase 1 — Beertio POC (Active)

- Single food item: Beer
- Multi-color vector icon (data-driven rendering)
- Widget with glance view showing: food icon + unit count (e.g., "2.7")
- Data source: daily calories from device
- Live updates while widget is visible (timer-based temporal events)
- Display only — no user interaction
- Generic abstractions in place (`FoodItem`, `FoodIconRenderer`, `AppSettings`)
- Selected item hardcoded to beer — no UI selector

### Phase 2 — Structural Hardening

- Finalize data format and renderer interface
- Ensure layout scales across device screen sizes
- Add unit tests where supported
- No new user-visible features

### Phase 3 — Multi-Item Expansion

- Add hard-coded food items (pizza, donut, etc.)
- SVG pipeline used for each new icon
- Expose item selector in settings UI
- Per-item default calorie values

### Phase 4 — Rename to Foodtio

- Rename `BeertioApp`/`BeertioView`/`BeertioGlanceView` classes to new brand
- Update Connect IQ store listing, screenshots, description
- Beer remains the default selected item
