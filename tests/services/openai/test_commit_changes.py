import unittest
from unittest.mock import patch, MagicMock
from services.openai.commit_changes import chat_with_agent
from services.github.github_types import BaseArgs

class TestChatWithAgent(unittest.TestCase):

    @patch('services.openai.commit_changes.create_openai_client')
    @patch('services.openai.commit_changes.count_tokens')
    def test_chat_with_agent(self, mock_count_tokens, mock_create_openai_client):
        # Mock the count_tokens function
        mock_count_tokens.return_value = 10

        # Mock the OpenAI client and its response
        mock_client = MagicMock()
        mock_create_openai_client.return_value = mock_client
        mock_completion = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_choice = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_choice.message.tool_calls = None

        messages = [{"role": "user", "content": "user input"}]
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

        result = chat_with_agent(messages, base_args, mode="commit")

        # Assertions
        self.assertEqual(result[0], messages)
        self.assertEqual(result[1], [])
        self.assertIsNone(result[2])
        self.assertIsNone(result[3])
        self.assertEqual(result[4], 10)
        self.assertEqual(result[5], 10)
        self.assertFalse(result[6])
        mock_count_tokens.assert_called()
        mock_create_openai_client.assert_called()
        mock_client.chat.completions.create.assert_called_once_with(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "user input"},
            ],
            model='gpt-4-0314',
            n=1,
            temperature=0.7,
            timeout=60,
            tools=[],
            tool_choice="auto",
            parallel_tool_calls=False,
        )

if __name__ == '__main__':
    unittest.main()
