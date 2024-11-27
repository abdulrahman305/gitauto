import unittest
from unittest.mock import patch, MagicMock
from services.openai.vision import describe_image

class TestDescribeImage(unittest.TestCase):

    @patch('services.openai.vision.create_openai_client')
    def test_describe_image(self, mock_create_openai_client):
        # Mock the OpenAI client and its response
        mock_client = MagicMock()
        mock_create_openai_client.return_value = mock_client
        mock_completion = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_completion.choices[0].message.content.strip.return_value = "Image description"

        base64_image = "base64encodedimage"

        response = describe_image(base64_image)

        # Assertions
        self.assertEqual(response, "Image description")
        mock_create_openai_client.assert_called_once()
        mock_client.chat.completions.create.assert_called_once_with(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe the image.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "auto",
                            },
                        },
                    ],
                },
            ],
            model='gpt-4-0314',
            n=1,
            temperature=0.7,
        )

if __name__ == '__main__':
    unittest.main()
