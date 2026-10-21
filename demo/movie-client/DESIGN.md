# CinemaFlow booking interface

Scope: the standalone movie client's static HTML/CSS/JavaScript. APIShield workspace styling is independent.

## Approved direction

A booking-first cinema interface inspired by the supplied reference: show selection left, auditorium centre, booking and payment summary right. Omit posters, cast, decorative movie banners and payment-disclaimer wording. Keep actual show data, the existing booking endpoints and independent provider controls. Do not introduce dates, showtimes, fees or discounts that the provider does not supply.

## Visual tokens

| Token | Dark | Light |
|---|---|---|
| Page | `#121313` | `#ffffff` |
| Surface | `#1c1e1e` | `#f6f7f5` |
| Field | `#141616` | `#ffffff` |
| Text | `#f3f3ef` | `#232721` |
| Secondary text | `#aaaead` | `#636b61` |
| Border | `#343837` | `#dce0d7` |
| Accent fill | `#f2d86b` | `#ead052` |
| Accent text | `#f2d86b` | `#796514` |
| Text on accent | `#25220f` | `#29240c` |

Open Sans is self-hosted with its existing OFL license. Surface radius is 16px. Default theme is dark, and the header toggle persists an explicit choice in localStorage. Storage failure must not disable the toggle. Apply the saved theme before CSS paints.

## Layout and behaviour

- Three columns above 1000px; selection/auditorium with a full-width two-column summary below at tablet widths; one reading-order column on mobile.
- Seats use chair geometry, row letters, an aisle and numbers, with visible selected and booked states. Preserve backend seat identities; unavailable seats are disabled. Selected seats update count, ticket chips and exact integer-paise totals immediately.
- Confirming a booking locks selection and provider mutations. Successful confirmation retains the ticket, reference and actual paid total; booked seats become unavailable. Selecting another seat starts a new selection.
- Movie/theatre/showtime controls use only current provider data. Loading, empty and connection-error states remain actionable.
- Provider controls stay in a separate keyboard-accessible tab. Arrow keys, Home/End, visible focus, accessible seat names and reduced-motion preferences are supported.
- Use small ticket-chip feedback and control transitions. No motion dependency or external UI library is required.
