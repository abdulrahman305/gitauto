import unittest
from unittest.mock import patch, MagicMock
from services.github.github_manager import GitHubManager

class TestGitHubManager(unittest.TestCase):

    @patch('services.github.github_manager.requests.get')
    def test_get_user_repos_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{'name': 'repo1'}, {'name': 'repo2'}]
        mock_get.return_value = mock_response

        github_manager = GitHubManager('test_token')
        repos = github_manager.get_user_repos('test_user')

        self.assertEqual(len(repos), 2)
        self.assertEqual(repos[0]['name'], 'repo1')
        self.assertEqual(repos[1]['name'], 'repo2')

    @patch('services.github.github_manager.requests.get')
    def test_get_user_repos_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        github_manager = GitHubManager('test_token')
        repos = github_manager.get_user_repos('test_user')

        self.assertEqual(repos, [])

    @patch('services.github.github_manager.requests.post')
    def test_create_repo_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'name': 'new_repo'}
        mock_post.return_value = mock_response

        github_manager = GitHubManager('test_token')
        repo = github_manager.create_repo('new_repo')

        self.assertEqual(repo['name'], 'new_repo')

    @patch('services.github.github_manager.requests.post')
    def test_create_repo_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        github_manager = GitHubManager('test_token')
        repo = github_manager.create_repo('new_repo')

        self.assertIsNone(repo)

if __name__ == '__main__':
    unittest.main()
