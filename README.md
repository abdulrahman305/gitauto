# Code Monkey AI

## What we do

We provide an AI agent that automatically generates pull requests from issues for backend code, enabling engineers to concentrate on core development.

## Who we target

Here is the list of our ICP (Ideal Customer Profile):

- **Platform**: GitHub users not GitLab or Bitbucket users
- **Size**: Individual developers or small teams in SMEs (Small and Medium-sized Enterprises) less than 100 employees not large enterprises due to compliance, security, and long sales cycle.
- **Geolocation**: San Francisco Bay Area in the United States
- **Language**: Backend code like Python and JavaScript / TypeScript

## What we measure

- **Merge Rate**: Aim for 90% (PRs merged / PRs created).
- **Churn Rate**: Aim for <5% (Unsubscriptions / (exisiting subscriptions + new subscriptions)).

## What the user workflow is

### 1. User preparation

First, users need to take the following steps to use our service:

- **User**: Visit our homepage or GitHub marketplace.
- **User**: Sign up with GiHub using the GitHub Authentication API.
- **User**: Install our app to repositories where the user wants to.

### 2. Demonstration on installation

Then, we demonstrate how to create a pull request from an issue:

- **AI**: Automatically creates an issue with a template in the repository.
- **AI**: Assigns itself as the assignee for that issue.
- **AI**: Reads the issue and comment on its current understanding of the issue.
- **AI**: Proposes a solution to that issue.
- **AI**: Presents a link to begin creating a PR.

### 3. Create an issue - Agree on a solution

- **User**: Assigns our AI to an issue. (The AI won't do anything until it's assigned so as not to disturb the user.)
- **AI**: Reads the issue and comment on its current understanding of the issue.
- **AI**: Proposes a solution to that issue.
- **AI**: Presents a link to begin creating a PR.
- **User**: Comments back to the AI if there's any disagreement.
- **User**: Clicks the link if the user agrees with the AI's proposal.

### 4. Create a PR - Ask for a review

- **AI**: Creates a new branch for that issue.
- **AI**: Inputs the content of that issue (text only).
- **AI**: Inputs the file tree of the repository.
- **AI**: Reads any files that seem relevant.
- **AI**: Suggests code changes in `the Unified Diff Format with no context lines`.
- **AI**: Double check for unnecessary lines that could cause bugs
- **AI**: Patches the code with the suggested changes.
- **AI**: Stages those file changes to the local branch.
- **AI**: Commits those file changes with a message in a format (e.g. `AI: Fixes #123: Add a new feature`) to the local branch.
- **AI**: Pushes those files to the remote branch from the local branch.
- **AI**: Identifies the base branch such as `main`.
- **AI**: Creates a new pull request to that base branch.
- **AI**: Write a description of that pull request in a format.
- **AI**: Assigns the user as a reviewer who clicked the link.

### 5. Review the PR - Merge the PR

- **User**: Reviews the PR.
- **User**: Comments on the PR if there's any disagreement.
- **AI**: Reads the comment and comments back to the user if there's any ambiguity.
- **AI**: Makes extra commits based on the user's comments.
- **User**: Approves the PR if the user is satisfied with the changes.
- **User**: Merges the PR if the user is satisfied with the changes.

## How to develop locally

### Tunnel to localhost with ngrok

1. Run `ngrok http --config=ngrok.yml --domain=gitauto.ngrok.dev 8000`.
2. ngrok will generate a URL `https://gitauto.ngrok.dev` that tunnels to `http://localhost:8000`.
3. Use `https://gitauto.ngrok.dev` as the webhook URL in the GitHub app settings.
4. You can check this setting in ngrok dashboard at `https://dashboard.ngrok.com/cloud-edge/domains`.

### Create a virtual environment

1. Run `python3 -m venv venv` to create a virtual environment.
2. Run `source venv/bin/activate` to activate the virtual environment. You will see `(venv)` in the terminal.
3. Note that you need to activate the virtual environment every time you open a new terminal.

### How to run the code

1. Run `pip install -r requirements.txt` to install the dependencies.
2. Ask for the `.env` file from the team and put it in the root directory.
3. Run `uvicorn main:app --reload --port 8000` to start the ASGI server and run `main.py` with `app` as the FastAPI instance. `--reload` is for auto-reloading the server when the code changes.

### How to encode a GitHub app private key to base64

GitHub app private key is in `.env` file. So basically you don't need to do this. But if you need to do this, follow the steps below. (Like when you create a new GitHub app and need to encode the private key to base64.)

1. Run `base64 -i prgent.2024-02-14.private-key.pem` to encode the private key to base64.
2. Copy the output and paste it in the `PRIVATE_KEY` field in the `.env` file.

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
