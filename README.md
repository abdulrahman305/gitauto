# issue-to-pr

## What we do

We provide an AI agent that automatically generates pull requests from issues for backend code, enabling engineers to concentrate on core development.

## What the workflow is

### User preparation

- User: Visit the homepage or GitHub marketplace.
- User: Sign up with GiHub using the GitHub Authentication API.
- User: Install our app to repositories where the user wants to.

### Iterration thereafter

- AI: Automatically picks the most recent unclosed GitHub issue.
- AI: Assigns itself as the assignee for that issue.
- AI: Creates a new branch for that issue.
- AI: Inputs the content of that issue (text only).
- AI: Searches 5 related files in the repository based on the input.
- AI: Writes code to resolve the issue.
- AI: Double check for unnecessary lines that could cause bugs
- AI: Turns that code into files.
- AI: Commits those files.
- AI: Identifies the main branch.
- AI: Creates a new pull request.
- AI: Write a description of that pull request in xxx format

## What the tech stack is

### Application

- Main: Python
- Framework: Fast API
- Runtime: Uvicorn
- Hosting: AWS Lambda?
- DB: Supabase?
- Payment: Stripe
- Unit Testing: Pytest?

### Homepage

- Main: TypeScript and React
- CSS: Tailwind CSS
- Framework: Next.js
- Hosting: Vercel
- Payment: Stripe
- DB: Supabase
- Unit Testing: Jest
- E2E Testing: Playwright

### Sales

- Outbound Email: Artisan AI
- Outbound LinkedIn:
- Twitter:
- Scheduling: Calendly
