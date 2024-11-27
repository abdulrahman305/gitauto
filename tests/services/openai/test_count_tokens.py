import unittest
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from services.openai.count_tokens import count_tokens

class TestCountTokens(unittest.TestCase):

    def test_count_tokens(self):
        messages = [
            ChatCompletionMessageParam(role="user", content="Hello, how are you?"),
            ChatCompletionMessageParam(role="assistant", content="I'm good, thank you!"),
        ]
        result = count_tokens(messages)
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)

if __name__ == '__main__':
    unittest.main()
