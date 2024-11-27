import unittest
from unittest.mock import patch, MagicMock
from services.openai.chat import chat_with_ai

class TestChatWithAI(unittest.TestCase):

    @patch('services.openai.chat.create_openai_client')
    @patch('services.openai.chat.truncate_message')
    def test_chat_with_ai(self, mock_truncate_message, mock_create_openai_client):
        # Mock the truncate_message function
        mock_truncate_message.return_value = "truncated user input"

        # Mock the OpenAI client and its response
        mock_client = MagicMock()
        mock_create_openai_client.return_value = mock_client
        mock_completion = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_completion.choices[0].message.content = "AI response"

        system_input = "system input"
        user_input = "user input"

        response = chat_with_ai(system_input, user_input)

        # Assertions
        self.assertEqual(response, "AI response")
        mock_truncate_message.assert_called_once_with(user_input)
        mock_create_openai_client.assert_called_once()
        mock_client.chat.completions.create.assert_called_once_with(
            messages=[
                {"role": "user", "content": system_input},
                {"role": "user", "content": "truncated user input"},
            ],
            model='gpt-4-0314',
            n=1,
        )

if __name__ == '__main__':
    unittest.main()
