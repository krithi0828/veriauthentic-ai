# VeriAuthentic AI — Visual Design System Specification

## Overview
The VeriAuthentic AI Design System provides a modern, high-contrast, accessible visual hierarchy tailored for product authenticity verification. Designed with the polish of Stripe, Linear, Vercel, and modern fintech platforms, it supports dark and light modes with seamless transitions and 100% progressive enhancement.

---

## 1. Color Palette & Tokens

### Base Theme Surfaces
- **Dark Mode (Default)**:
  - Body Background: `#0b0f19` (Deep Obsidian Slate)
  - Surface Card: `#111827` (Rich Graphite)
  - Raised Surface: `#1f2937`
  - Subtle Border: `rgba(255, 255, 255, 0.07)`
  - Medium Border: `rgba(255, 255, 255, 0.12)`
- **Light Mode**:
  - Body Background: `#f8fafc` (Cool Off-White)
  - Surface Card: `#ffffff` (Pure White)
  - Raised Surface: `#f1f5f9`
  - Subtle Border: `#e2e8f0`
  - Medium Border: `#cbd5e1`

### Brand & Accent Gradients
- **Primary Brand Gradient**: `linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)` (Indigo to Violet)
- **Brand Primary Accent**: `#6366f1`
- **Cyan Secondary Accent**: `#06b6d4`

### Semantic Risk Bands (Always paired with text labels and Lucide SVG icons)
- **Low Risk (0–25%)**: Emerald `#10b981` (Badge: `.badge-low`)
- **Moderate Risk (26–50%)**: Amber `#f59e0b` (Badge: `.badge-moderate`)
- **High Risk (51–75%)**: Orange `#f97316` (Badge: `.badge-high`)
- **Critical Risk (76–100%)**: Red `#ef4444` (Badge: `.badge-critical`)

---

## 2. Typography Scale

- **Sans-Serif Font**: `Inter`, system-ui, -apple-system, sans-serif
- **Monospace Font**: `JetBrains Mono`, SFMono-Regular, monospace
- **Hierarchy Scale**:
  - `h1`: `clamp(2.5rem, 4.5vw, 3.75rem)` (48px – 60px), line-height `1.1`, tracking `-0.04em`
  - `h2`: `1.875rem` (30px), tracking `-0.025em`
  - `h3`: `1.5rem` (24px)
  - `h4`: `1.25rem` (20px)
  - `h5`: `1.0rem` (16px)
  - Body: `0.875rem` (14px), line-height `1.6`
  - Micro / Captions: `0.75rem` (12px)

---

## 3. Component Architecture & Radii

- **Border Radii Grid**:
  - `--radius-sm`: `8px`
  - `--radius-md`: `12px`
  - `--radius-lg`: `16px`
  - `--radius-xl`: `24px`
  - `--radius-full`: `9999px`

- **Interactive Components**:
  - `.btn-primary`: Brand gradient background, white text, subtle hover lift and glow shadow.
  - `.btn-secondary`: Raised surface, border medium stroke, hover transition.
  - `.btn-ghost`: Transparent background, subtle text hover.
  - `.form-input-mono`: Monospace uppercase auto-formatting mask for 12-char codes (`AUTH-XXXX-XXXX`).
  - `.segmented-control`: Rounded toggle switcher for multi-mode views.
  - `.skip-link`: Accessible keyboard skip navigation anchor.
  - `.skeleton`: Animated shimmer loading state for async updates.
  - `#js-error-banner`: Non-blocking global JS fallback banner.

---

## 4. Accessibility & Progressive Enhancement (WCAG 2.2 AA)

- **Contrast Ratios**: All text meets or exceeds contrast ratio of `4.5:1`.
- **Keyboard Navigation**: Complete focus ring styling (`:focus-visible`) across all buttons, inputs, and links.
- **Screen Reader Landmarks**: `<header>`, `<nav>`, `<main>`, `<footer>`, and `aria-label` attributes configured.
- **Progressive Enhancement Guarantee**: Content is 100% visible and interactive without JavaScript. Animation reveal rules are strictly scoped to `<html class="js">`.
