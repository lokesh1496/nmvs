---
name: NMVS Network Visibility Console
colors:
  surface: '#f8f9ff'
  surface-dim: '#c6dcfa'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eef4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dbe9ff'
  surface-container-highest: '#d1e4ff'
  on-surface: '#051d33'
  on-surface-variant: '#3c494b'
  inverse-surface: '#1c3249'
  inverse-on-surface: '#eaf1ff'
  outline: '#6c7a7b'
  outline-variant: '#bbc9cb'
  surface-tint: '#006971'
  primary: '#006971'
  on-primary: '#ffffff'
  primary-container: '#22c7d6'
  on-primary-container: '#004e55'
  inverse-primary: '#43d9e8'
  secondary: '#2a57c2'
  on-secondary: '#ffffff'
  secondary-container: '#6a91fe'
  on-secondary-container: '#002873'
  tertiary: '#006a66'
  on-tertiary: '#ffffff'
  tertiary-container: '#3ec8c1'
  on-tertiary-container: '#00504c'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#89f2ff'
  primary-fixed-dim: '#43d9e8'
  on-primary-fixed: '#001f23'
  on-primary-fixed-variant: '#004f56'
  secondary-fixed: '#dbe1ff'
  secondary-fixed-dim: '#b4c5ff'
  on-secondary-fixed: '#00174a'
  on-secondary-fixed-variant: '#003ea7'
  tertiary-fixed: '#75f7ef'
  tertiary-fixed-dim: '#55dad2'
  on-tertiary-fixed: '#00201e'
  on-tertiary-fixed-variant: '#00504c'
  background: '#f8f9ff'
  on-background: '#051d33'
  surface-variant: '#d1e4ff'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 2rem
    fontWeight: '700'
    lineHeight: 2.5rem
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Inter
    fontSize: 1.5rem
    fontWeight: '700'
    lineHeight: 2rem
    letterSpacing: -0.015em
  headline-lg:
    fontFamily: Inter
    fontSize: 1.5rem
    fontWeight: '600'
    lineHeight: 2rem
    letterSpacing: -0.015em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 1.25rem
    fontWeight: '600'
    lineHeight: 1.75rem
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 1.125rem
    fontWeight: '600'
    lineHeight: 1.5rem
    letterSpacing: -0.01em
  title-sm:
    fontFamily: Inter
    fontSize: 0.875rem
    fontWeight: '600'
    lineHeight: 1.25rem
    letterSpacing: -0.005em
  body-lg:
    fontFamily: Inter
    fontSize: 1rem
    fontWeight: '400'
    lineHeight: 1.5rem
    letterSpacing: 0em
  body-md:
    fontFamily: Inter
    fontSize: 0.875rem
    fontWeight: '400'
    lineHeight: 1.25rem
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 0.75rem
    fontWeight: '400'
    lineHeight: 1rem
    letterSpacing: 0.01em
  label-md:
    fontFamily: Inter
    fontSize: 0.75rem
    fontWeight: '600'
    lineHeight: 1rem
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Inter
    fontSize: 0.6875rem
    fontWeight: '500'
    lineHeight: 0.875rem
    letterSpacing: 0.03em
  code-sm:
    fontFamily: Inter
    fontSize: 0.75rem
    fontWeight: '500'
    lineHeight: 1rem
    letterSpacing: -0.01em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-desktop: 1.25rem
  margin: 1rem
  margin-desktop: 1.5rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.875rem
  space-lg: 1.25rem
  space-xl: 1.75rem
  space-2xl: 2.5rem
---

## Brand & Style

The design system establishes a high-precision, mission-critical workspace for network engineering, packet-inspection forensics, and telemetry observability. Designed for systems operators and network reliability engineers, the interface bridges dense technical telemetry with an ergonomic, low-strain physical presence.

The visual style blends soft glassmorphism and restrained neumorphic tactile modeling against a calming, muted slate-blue workbench canvas. Dense data structures are housed within smoothly extruded card containers that employ dual-source directional diffusion (ambient top-left highlight paired with a deep bottom-right drop shadow). Deep midnight-navy hero modules and top-level navigation anchor high-priority alerts, while vibrant electric cyan and teal telemetry signals glow with high contrast, enabling immediate fault isolation and topology scanning.

## Colors

The palette balances soft physical lighting with luminous digital instrumentation.

- **Workbench Canvas (`#879CB8`):** An atmospheric slate-blue background that prevents eye fatigue while providing the mid-tone foundation required for subtle light extrusion.
- **Header & Critical Deep Modules (`#17233F` to `#202D4B`):** Deep navy tones reserved for top navigation bars, terminal-grade packet traces, active dark-card highlights, and global filters.
- **Card Surfaces (`#F4F7FC` to `#E8EEF7`):** Pristine, high-legibility light slate containers with gentle white bevel highlights (`#FFFFFF` at 60% opacity) on the upper edge and soft ambient shading underneath.
- **Vibrant Instrumentation Accents (`#22C7D6` Cyan & `#21B7B0` Teal):** Used strictly for dynamic signals, active telemetry sparklines, circular throughput gauges, and healthy latency indicators.
- **Secondary Blue (`#547CE8`):** Provides anchor coloring for secondary series, interactive toggles, time-window selectors, and protocol chips.
- **Telemetry Semantics:** Incident Red (`#FF5C6C`), Warning Amber (`#F5A623`), and Idle Slate (`#9AAEC9`).

## Typography

Typography relies entirely on Inter configured with tight tracking and calibrated vertical alignment to optimize rapid scanning of metrics, interface rates, IP addresses, and throughput statistics.

Tabular figures (`font-variant-numeric: tabular-nums`) must be activated across all telemetry readouts, timestamps, payload counters, and data tables to preserve vertical column alignment during live network streaming updates. Metrics titles utilize medium and semibold weights with subdued slate values (`#6C82A3` on light containers; `#94A7C6` on navy cards), reserving pure white and intense carbon for real-time values.

## Layout & Spacing

The system is constructed around a structured 12-column grid anchored inside a contained frame with consistent edge padding.

- **Desktop (1280px+):** Full 12-column layout with 20px (`1.25rem`) gutters and 24px (`1.5rem`) canvas margins. Heavy cards align symmetrically to display multiple parallel streams: left telemetry panel (3 columns), center traffic flow distribution (5 columns), and right topology/cost distribution (4 columns).
- **Tablet (768px – 1279px):** 8-column layout with 16px (`1rem`) gutters. Sub-panels stack into dual-column cards, collapsing sparkline histories into unified tabbed modules.
- **Mobile (<768px):** 4-column layout with 16px (`1rem`) outer margins. Cards convert to full-width containers with horizontal carousel scroll for historical bar metrics and topology rings.

Spacing tokens prioritize dense operational layouts: internal module padding is calibrated at `space-md` (14px) and `space-lg` (20px), ensuring peak visual throughput without card overcrowding.

## Elevation & Depth

Visual hierarchy combines directional extruded shadows and soft ambient backdrops to establish physical separation from the slate canvas.

- **Canvas Level (Elevation 0):** The base slate substrate (`#879CB8`).
- **Elevated Light Containers (Elevation 1):** Extruded using dual soft shadows:
  - Top-left light reflection: `-4px -4px 12px 0px rgba(255, 255, 255, 0.65)`
  - Bottom-right shadow drop: `8px 12px 24px -4px rgba(32, 45, 75, 0.18)`
  - Edge treatment: crisp 1px perimeter border rendered in `rgba(255, 255, 255, 0.40)` for subtle refraction.
- **Navy Hero Module (Elevation 2 - Accent Depth):** Uses a deep navy backdrop (`#17233F`) with an inner top specular glow (`inset 0 1px 1px 0 rgba(255, 255, 255, 0.15)`) and a deep outer diffuse shadow: `0 16px 32px -6px rgba(17, 24, 39, 0.40)`.
- **Sunken Interactive Wells (Elevation -1):** Inset controls such as search fields, de-selected pills, and track sliders use an inner shadow (`inset 2px 2px 5px rgba(20, 30, 50, 0.14), inset -2px -2px 5px rgba(255, 255, 255, 0.5)`).
- **Glow & Active Signals:** High-priority cyan lines and radar nodes emit an optical bloom (`box-shadow: 0 0 12px rgba(34, 199, 214, 0.45)`).

## Shapes

The interface is defined by soft, organic geometric corners that counterbalance rigid operational data tables.

- **Large Dashboard Cards:** Radii set to 24px (`rounded-xl` / 1.5rem), creating an inviting, hardware-like console chassis.
- **Pills, Badges, and Filter Caps:** Fully rounded pill shapes (`9999px`) used for sub-navigation, filter chips, state badges, and toggle switches.
- **Buttons and Inputs:** 12px (`0.75rem`) corner radius for standard touch and click affordances.
- **Micro UI (Tooltips, Checkboxes, Micro-tags):** 6px to 8px radius to retain crisp definition at high pixel densities.

## Components

### Buttons
- **Primary Action (Cyan Glow):** Solid vibrant cyan (`#22C7D6`) background, navy text (`#0D1A30`), font weight 600. Employs a subtle bottom shadow (`0 4px 12px rgba(34, 199, 214, 0.35)`). Hover increases brightness and expands blur.
- **Secondary (Dark Navy / Glass):** Dark navy background (`#202D4B`) with crisp white text and a 1px border (`rgba(255, 255, 255, 0.15)`).
- **Subtle / Soft Button:** Light slate surface (`#E8EEF7`) with dual soft extruded shadows, providing a tactile, tactile press-down transition to an inset shadow when active.

### Segmented Controls & Pills
- Pill containers feature sunken wells (`#DDE5F2` or `#131C33` in dark headers) hosting pill segments.
- The active segment transitions to a soft white card surface (`#FFFFFF` with `0 2px 8px rgba(0,0,0,0.08)`) or luminous cyan-bordered navy badge (`#202D4B` + cyan outline) with medium weight text.

### Cards & Module Containers
- **Standard Telemetry Card:** Light slate-white gradient (`#F4F7FC` to `#EDF2FA`) with 24px rounded corners and dual soft shadows.
- **Deep Signal Card:** Midnight navy (`#17233F` to `#1D2A47`) with deep ambient drop shadow, integrated cyan sparklines, and white/cyan numeric readouts.
- All cards contain structured header bars: left-aligned section title (`title-sm`), right-aligned numeric badge or action pill.

### Charts & Data Visualizations
- **Bar Charts:** Rounded column tops (minimum 4px cap radius) in alternating alternating teal (`#21B7B0`) and primary cyan (`#22C7D6`), with inactive months/intervals rendered in muted steel blue (`#C2D0E4`).
- **Telemetry Line/Sparkline:** Smooth splines in vibrant cyan with soft gradient fills beneath (`rgba(34, 199, 214, 0.25)` tapering to transparent) and circular indicator nodes carrying radial cyan drop glows.
- **Radar & Donut Charts:** Thick track rings with clean segmented gaps, colored in high-contrast cyan, secondary blue, and slate-grey baseline tracks.

### Input Fields & Selectors
- Recessed inset containers with subtle inward drop shadow and pale slate backgrounds (`#E3ECF7`).
- Active focus displays a 1.5px outer ring in glowing cyan (`#22C7D6`) with a 4px soft outer bloom. Placeholder text rendered in neutral slate (`#7D91AD`).

### Status Badges & Indicators
- Live status pills (Healthy, Degraded, Critical, Rerouted) featuring a 6px breathing dot indicator accompanied by compact uppercase `label-sm` text.
- Healthy uses `#21B7B0` teal on soft mint-tinted wells; Critical utilizes `#FF5C6C` on soft crimson-tinted wells.