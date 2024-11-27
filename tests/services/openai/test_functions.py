import unittest
from unittest.mock import patch, MagicMock
from services.openai.functions.functions import (
    commit_changes_to_remote_branch,
    get_remote_file_content,
    search_remote_file_contents,
    update_comment,
)
from services.github.github_types import BaseArgs

class TestFunctions(unittest.TestCase):

    @patch('services.openai.functions.functions.commit_changes_to_remote_branch')
    def test_commit_changes_to_remote_branch(self, mock_commit_changes):
        mock_commit_changes.return_value = "Commit successful"
        base_args = BaseArgs(
            owner="owner",
            repo="repo",
            is_fork=False,
            base_branch="main",
            new_branch="feature",
            comment_url="http://example.com",
            pr_body="PR body",
            token="token"
        )
        result = commit_changes_to_remote_branch("diff", "file_path", base_args)
        self.assertEqual(result, "Commit successful")
        mock_commit_changes.assert_called_once_with("diff", "file_path", base_args)

    @patch('services.openai.functions.functions.get_remote_file_content')
    def test_get_remote_file_content(self, mock_get_content):
        mock_get_content.return_value = "File content"
        base_args = BaseArgs(
            owner="owner",
            repo="repo",
            is_fork=False,
            base_branch="main",
            new_branch="feature",
            comment_url="http://example.com",
            pr_body="PR body",
            token="token"
        )
        result = get_remote_file_content("file_path", base_args)
        self.assertEqual(result, "File content")
        mock_get_content.assert_called_once_with("file_path", base_args)

    @patch('services.openai.functions.functions.search_remote_file_contents')
    def test_search_remote_file_contents(self, mock_search_content):
        mock_search_content.return_value = "Search results"
        base_args = BaseArgs(
            owner="owner",
            repo="repo",
            is_fork=False,
            base_branch="main",
            new_branch="feature",
            comment_url="http://example.com",
            pr_body="PR body",
            token="token"
        )
        result = search_remote_file_contents("query", base_args)
        self.assertEqual(result, "Search results")
        mock_search_content.assert_called_once_with("query", base_args)

    @patch('services.openai.functions.functions.update_comment')
    def test_update_comment(self, mock_update_comment):
        mock_update_comment.return_value = "Update successful"
        base_args = BaseArgs(
            owner="owner",
            repo="repo",
            is_fork=False,
            base_branch="main",
            new_branch="feature",
            comment_url="http://example.com",
            pr_body="PR body",
            token="token"
        )
        result = update_comment("body", base_args)
        self.assertEqual(result, "Update successful")
        mock_update_comment.assert_called_once_with("body", base_args)

if __name__ == '__main__':
    unittest.main()
