from datetime import datetime
import json
from typing import Any

# Local imports
from config import (
    EXCEPTION_OWNERS,
    GITHUB_APP_USER_NAME,
    IS_PRD,
    STRIPE_PRODUCT_ID_FREE,
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY,
)
from services.github.comment_manager import reply_to_comment
from services.github.github_manager import (
    get_installation_access_token,
    get_remote_file_content,
    get_remote_file_tree,
    update_comment,
)
from services.github.github_types import Owner, PullRequest, Repository
from services.github.pulls_manager import get_pull_request_file_contents
from services.openai.commit_changes import chat_with_agent
from services.stripe.subscriptions import get_stripe_product_id
from services.supabase import SupabaseManager
from services.supabase.owers_manager import get_stripe_customer_id
from utils.colorize_log import colorize
from utils.progress_bar import create_progress_bar

supabase_manager = SupabaseManager(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY)


def handle_review_run(payload: dict[str, Any]) -> None:
    print("handle_review_run was called")

    # Extract review comment etc
    review: dict[str, Any] = payload["comment"]
    review_id: str = review["id"]
    review_path: str = review["path"]
    review_subject_type: str = review["subject_type"]
    review_line: int = review["line"]
    review_side: str = review["side"]
    review_position: int = review["position"]
    review_body: str = review["body"]
    review_comment = f"## Review Comment\n{review_path} Line: {review_line} Position: {review_position}\n{review_body}"

    # Extract repository related variables
    repo: Repository = payload["repository"]
    repo_name: str = repo["name"]
    is_fork: bool = repo["fork"]

    # Extract owner related variables
    owner: Owner = repo["owner"]
    owner_type: str = owner["type"]
    owner_id: int = owner["id"]
    owner_name: str = owner["login"]

    # Extract PR related variables
    pull_request: PullRequest = payload["pull_request"]
    pull_number: int = pull_request["number"]
    pull_title: str = pull_request["title"]
    pull_body: str = pull_request["body"]
    pull_url: str = pull_request["url"]
    pull_file_url: str = f"{pull_url}/files"
    head_branch: str = pull_request["head"]["ref"]  # gitauto/issue-167-20250101-155924
    pull_user: str = pull_request["user"]["login"]
    if pull_user != GITHUB_APP_USER_NAME:
        return  # Prevent GitAuto from jumping into others' PRs

    # Extract sender related variables and return if sender is GitAuto itself
    sender_id: int = payload["sender"]["id"]
    sender_name: str = payload["sender"]["login"]
    if sender_name == GITHUB_APP_USER_NAME:
        return  # Prevent infinite loops by self-triggering

    print(f"Payload: {json.dumps(payload, indent=2)}")

    # Extract other information
    installation_id: int = payload["installation"]["id"]
    token: str = get_installation_access_token(installation_id=installation_id)
    base_args: dict[str, str | int | bool] = {
        "owner_type": owner_type,
        "owner_id": owner_id,
        "owner": owner_name,
        "repo": repo_name,
        "is_fork": is_fork,
        "issue_number": pull_number,
        "pull_number": pull_number,
        "pull_title": pull_title,
        "pull_body": pull_body,
        "pull_url": pull_url,
        "pull_file_url": pull_file_url,
        "new_branch": head_branch,
        "base_branch": head_branch,  # Yes, intentionally set head_branch to base_branch because get_remote_file_tree requires the base branch
        "review_id": review_id,
        "review_path": review_path,
        "review_subject_type": review_subject_type,
        "review_line": review_line,
        "review_side": review_side,
        "review_position": review_position,
        "review_body": review_body,
        "review_comment": review_comment,
        "sender_id": sender_id,
        "sender_name": sender_name,
        "token": token,
    }

    # Return here if stripe_customer_id is not found
    stripe_customer_id: str | None = get_stripe_customer_id(owner_id=owner_id)
    if stripe_customer_id is None:
        return

    # Return here if product_id is not found or is in free tier
    product_id: str | None = get_stripe_product_id(customer_id=stripe_customer_id)
    is_paid = product_id is not None and product_id != STRIPE_PRODUCT_ID_FREE
    is_exception = owner_name in EXCEPTION_OWNERS
    if not is_paid and IS_PRD and not is_exception:
        msg = f"Skipping because product_id is not found or is in free tier. product_id: '{product_id}'"
        print(colorize(text=msg, color="yellow"))
        return

    # Get a review commented file
    msg = "Thanks for the feedback! Collecting info... 🕵️"
    comment_body = create_progress_bar(p=0, msg=msg)
    comment_url = reply_to_comment(base_args=base_args, body=comment_body)
    base_args["comment_url"] = comment_url
    review_file = get_remote_file_content(file_path=review_path, base_args=base_args)

    # Get changed files in the PR
    pull_files = get_pull_request_file_contents(url=pull_file_url, base_args=base_args)

    # Get the file tree in the root of the repo
    comment_body = "Checking out the file tree in the repo..."
    update_comment(body=comment_body, base_args=base_args, p=10)
    file_tree: str = get_remote_file_tree(base_args=base_args)

    # Plan how to fix the error
    comment_body = "Planning how to achieve your feedback..."
    update_comment(body=comment_body, base_args=base_args, p=20)
    today = datetime.now().strftime("%Y-%m-%d")
    input_message: dict[str, str] = {
        "pull_request_title": pull_title,
        "pull_request_body": pull_body,
        "review_comment": review_comment,
        "review_file": review_file,
        "pull_files": pull_files,
        "file_tree": file_tree,
        "today": today,
    }
    user_input = json.dumps(obj=input_message)

    # Update the comment if any obstacles are found
    comment_body = "Checking if I can solve it or if I should just hit you up..."
    update_comment(body=comment_body, base_args=base_args, p=30)
    messages = [{"role": "user", "content": user_input}]

    # NOTE: Disabled this ask back feature because it's not working as expected and GitAuto just responded like "I've done it" but code returned here.
    # (
    #     _messages,
    #     _previous_calls,
    #     _tool_name,
    #     _tool_args,
    #     _token_input,
    #     _token_output,
    #     is_commented,
    # ) = chat_with_agent(messages=messages, base_args=base_args, mode="comment")
    # if is_commented:
    #     return

    # Loop a process explore repo and commit changes until the ticket is resolved
    previous_calls = []
    retry_count = 0
    p = 40
    while True:
        # Explore repo
        (
            messages,
            previous_calls,
            tool_name,
            tool_args,
            _token_input,
            _token_output,
            is_explored,
        ) = chat_with_agent(
            messages=messages,
            base_args=base_args,
            mode="get",  # explore can not be used here because "search_remote_file_contents" can search files only in the default branch NOT in the branch that is merged into the default branch
            previous_calls=previous_calls,
        )
        comment_body = f"Calling `{tool_name}()` with `{tool_args}`..."
        update_comment(body=comment_body, base_args=base_args, p=p)
        p = min(p + 5, 95)

        # Search Google
        (
            messages,
            previous_calls,
            tool_name,
            tool_args,
            _token_input,
            _token_output,
            _is_searched,
        ) = chat_with_agent(
            messages=messages,
            base_args=base_args,
            mode="search",
            previous_calls=previous_calls,
        )
        if tool_name is not None and tool_args is not None:
            comment_body = f"Calling `{tool_name}()` with `{tool_args}`..."
            update_comment(body=comment_body, base_args=base_args, p=p)
            p = min(p + 5, 95)

        # Commit changes based on the exploration information
        (
            messages,
            previous_calls,
            tool_name,
            tool_args,
            _token_input,
            _token_output,
            is_committed,
        ) = chat_with_agent(
            messages=messages,
            base_args=base_args,
            mode="commit",
            previous_calls=previous_calls,
        )
        msg = f"Calling `{tool_name}()` with `{tool_args}`..."
        update_comment(body=comment_body, base_args=base_args, p=p)
        p = min(p + 5, 95)

        # If no new file is found and no changes are made, it means that the agent has completed the ticket or got stuck for some reason
        if not is_explored and not is_committed:
            break

        # If no files are found but changes are made, it might fall into an infinite loop (e.g., repeatedly making and reverting similar changes with slight variations)
        if not is_explored and is_committed:
            retry_count += 1
            if retry_count > 3:
                break
            continue

        # If files are found but no changes are made, it means that the agent found files but didn't think it's necessary to commit changes or fell into an infinite-like loop (e.g. slightly different searches)
        if is_explored and not is_committed:
            retry_count += 1
            if retry_count > 3:
                break
            continue

        # Because the agent is committing changes, keep doing the loop
        retry_count = 0

    # Create a pull request to the base branch
    msg = "Resolved your feedback! Looks good?"
    update_comment(body=msg, base_args=base_args)
    return
