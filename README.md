# Dundas East Animal Hospital — website concept

A responsive website redesign and interactive client payment portal demo, prepared by Bird E Consulting for discussion with Dundas East Animal Hospital. The second version migrates the complete original public page and article inventory; see [CONTENT-AUDIT.md](CONTENT-AUDIT.md).

## Demo features

- Original information retained across 16 published page routes and eight complete articles, including seven detailed services, all four doctors, hospital history, both locations, working hours and original Google review excerpts.
- Refreshed navigation, service directory, article layouts, doctor profiles, maps and click-to-call links. Original photos are hosted locally.
- Four illustrative pet products, category filters, cart quantities and totals.
- Fictional invoice lookup: `DEMO-1042`, client code `PET-2026`.
- Checkout simulation and demonstration receipt. **No payment processing, card fields, real invoices, orders, accounts, or personal data collection.**
- Visible service cards, eight fully visible client reviews, and readable article sections with clear headings. The Why Choose section uses six SVG-led dropdowns with a spacious desktop grid and stacked mobile layout. Opening hours, maps and archived source content also remain expandable. All original information remains available.
- SVG icons replace font-based pictographs and product emojis on all screen sizes.
- Keyboard-accessible tabs, responsive layouts, reduced-motion support and semantic HTML.

## Run

Run `node scripts/preview.mjs`, then open `http://127.0.0.1:4174/dundas-east-animal-hospital/`. Static output is committed, so GitHub Pages needs no build. Publish the root of `main`.

Regenerate the demo from the committed content snapshot with `python scripts/migrate_content.py`. Run `python scripts/validate_site.py` and `node --check app.js` before publishing.

## SEO and production handoff

Every page has a descriptive title, meta description, canonical URL, social metadata and one H1. Pages render their content in HTML without JavaScript. JSON-LD includes veterinary practice details, breadcrumbs and article dates. Original service and article slugs remain intact, with a production sitemap and a functional 404 page.

**The GitHub Pages demo deliberately uses `noindex,follow` and canonicals pointing to the corresponding original clinic URLs.** It is prepared for SEO at the clinic domain and does not compete with the live website. No rankings or rich-result eligibility are guaranteed.

Only when preparing the actual clinic-domain release, run `python scripts/migrate_content.py --production`. This removes the GitHub project-path prefix, enables indexing for real pages and adds the production sitemap to robots.txt. It keeps unfinished template-only pages excluded from indexing. Do not deploy that output to the GitHub project URL. Regenerate without `--production` for the demo.

Before a real migration, check the complete Search Console URL inventory and backlinks, retain server-side 301 redirects for any additional legacy variants, submit the sitemap, and confirm domain/DNS, robots and canonical behavior. The existing `/home/` alias canonicalizes to `/`. GitHub Pages is a demonstration host and does not provide a custom redirect engine.

## Content and assets

Content was captured from the public WordPress API at https://dundasvets.com/ on October 21, 2026. The committed `content/site-content.json` stores all original visible content with safe HTML; `content/original-content.json` provides a full text audit. The design retains original clinical copy without claiming to medically review it. Original unfinished templates are labelled for review, and conflicting Dundas weekday/Wednesday hours remain visible with a confirmation note. No hours, ratings, credentials or testimonials are invented. Review counts are labelled as a snapshot, not a live feed.

Clinic, doctor and article photography is copied from the original site's public assets into `assets/`. Fonts are DM Sans and Manrope from Google Fonts, with system fallbacks. Sample product illustrations are made in HTML/CSS. Sample product names and prices are invented, in CAD, and include any applicable taxes for demonstration purposes only.

## Before real launch

Have the clinic approve copy, products, pricing, taxation, pickup policies and imagery. Integrate a hosted payment provider with server-side invoice verification, verified payment webhooks and appropriate privacy controls. The demo is intentionally static and must not be used to accept actual payments.
