# Naming conventions

- Code, types, files, comments, docs, and commits are English.
- User-facing copy is Brazilian Portuguese.
- Components and types use PascalCase.
- Functions and runtime values use camelCase.
- Fixed configuration uses SCREAMING_SNAKE_CASE.
- Route and component folders use kebab-case.
- Ordinary component implementations use `<component>/index.tsx`.
- Component props use `types.ts` when needed.
- Domain types, enums, helpers, and services use lowercase kebab-case files.
- Use string enums for closed job, source, export, and transcript states.
- Import concrete modules; do not add barrel-only files.
