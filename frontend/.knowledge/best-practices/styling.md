# Styling

Use Tailwind utilities in the owning JSX. Shared visual recipes belong in a
shared component, not a global class or TypeScript string bucket.

`app/globals.css` contains the Tailwind import, Rune theme aliases, document
defaults, class-controlled dark mode, selection, focus, and reduced-motion
safety. Do not add CSS Modules or CSS-in-JS.

Use warm paper and white surfaces in Light. Use near-black and graphite in
Dark. Dark green carries primary text and the approved mark. Mint is reserved
for the primary action, selection, and focus. Status colors stay semantic.

Responsive layouts reflow instead of shrinking desktop canvases. Preserve the
composer action, queue status, transcript text, and touch targets first.
