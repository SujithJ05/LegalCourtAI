
import unittest
from unittest.mock import patch, MagicMock
from app import app
from core.trial_manager import TrialManager
from core import trial_store

@patch('utils.llm.run_ollama')
class TestTrialManager(unittest.TestCase):

    def setUp(self):
        trial_store.clear()
        self.case_facts = "Test case facts."

    def test_trial_manager_creation(self, mock_run_ollama):
        """Test that the TrialManager is created correctly."""
        manager = TrialManager(case_facts=self.case_facts)
        self.assertEqual(manager.case_facts, self.case_facts)
        self.assertIsNotNone(manager.plaintiff)
        self.assertIsNotNone(manager.defendant)
        self.assertIsNotNone(manager.judge)

    def test_run_trial_step_by_step(self, mock_run_ollama):
        """Test the full trial flow, mocking the LLM calls."""
        # Mock the return value of the LLM for each agent
        mock_run_ollama.return_value = "This is a mocked response."

        manager = TrialManager(case_facts=self.case_facts)
        manager.run_trial_step_by_step()

        # Check that the conversation history has been populated
        self.assertTrue(len(manager.conversation_history) > 0)

        # Check that the mock was called multiple times
        self.assertTrue(mock_run_ollama.call_count > 5)

@patch('utils.llm.run_ollama')
class TestApp(unittest.TestCase):

    def setUp(self):
        trial_store.clear()
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'supersecretkey'
        self.app = app.test_client()

    def test_index_route(self, mock_run_ollama):
        """Test the index route."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_start_trial_route_success(self, mock_run_ollama):
        """Test the start_trial route with valid data."""
        response = self.app.post('/start_trial', 
                                 json={"case_facts": "This is a test case with enough characters to pass validation."})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Trial initialized', response.get_json()['message'])

    def test_start_trial_route_failure(self, mock_run_ollama):
        """Test the start_trial route with invalid data."""
        response = self.app.post('/start_trial', json={"case_facts": "short"})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())

    def test_next_statement_route(self, mock_run_ollama):
        """Test the next_statement route."""
        mock_run_ollama.return_value = "Mocked AI statement."

        with self.app as client:
            client.post('/start_trial', 
                      json={"case_facts": "This is a test case for the next statement route, which needs to be long enough."})

            # Then, get the next statement
            response = client.post('/next_statement')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertIn('speaker', data)
            self.assertIn('statement', data)
            self.assertEqual(data['statement'], "Mocked AI statement.")

if __name__ == '__main__':
    unittest.main()
