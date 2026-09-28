# Second Shift: refurbished laptop store (homepage UI)

A static homepage design for an e-commerce store selling refurbished laptops. Open `index.html` in a browser; no build step is needed.

- `index.html`: page markup, including the reusable laptop drawing (an SVG symbol recoloured per product with `--lid`, `--deck` and `--screen`)
- `styles.css`: design tokens and components
- `app.js`: filtering by need, search, add to cart with confirmation, trade-in estimate, mobile menu

## Placeholders to replace
- Brand name "Second Shift" and the "2" logo mark
- Product names, specs, prices, battery figures and stock count
- Hero figures ("42 points", "up to 60% less") and the CO₂ figure
- Reviews: these are sample text, not real customers
- Trade-in prices: `base`, `ageFactor` and `condFactor` in `app.js` are made-up numbers
- Laptop drawings: swap in real product photos when you have them
- Cart, search and forms are front-end only; connect them to your store platform
