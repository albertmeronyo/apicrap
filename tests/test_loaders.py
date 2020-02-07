import unittest
import six
from mock import patch
from os import path

from grlc.fileLoaders import LocalLoader, GithubLoader, URLLoader
from grlc.queryTypes import qType

from tests.mock_data import mock_requestsGithub, mock_requestsUrl


class TestGithubLoader(unittest.TestCase):
    def setUp(self):
        self.patcher = patch('requests.get', side_effect=mock_requestsGithub)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    @classmethod
    @patch('github.Github.get_repo', return_value=[])
    def setUpClass(self, github_get_repo_patch):
        self.user = 'fakeuser'
        self.repo = 'fakerepo'
        self.loader = GithubLoader(self.user, self.repo, subdir=None, sha=None, prov=None)

    def test_fetchFiles(self):
        files = self.loader.fetchFiles()

        # Should return a list of file items
        self.assertIsInstance(files, list, "Should return a list of file items")

        # Should have N files (where N=9)
        self.assertEqual(len(files), 9, "Should return correct number of files")

        # File items should have a download_url
        for fItem in files:
            self.assertIn('download_url', fItem, "File items should have a download_url")

    def test_getRawRepoUri(self):
        repoUri = self.loader.getRawRepoUri()

        # Should be a string
        self.assertIsInstance(repoUri, six.string_types, "Should be a string")

        # For URI shoud contain user / repo
        self.assertIn(self.user, repoUri, "Should contain user")
        self.assertIn(self.repo, repoUri, "Should contain repo")

    def test_getTextFor(self):
        files = self.loader.fetchFiles()

        # the contents of each file
        for fItem in files:
            text = self.loader.getTextFor(fItem)

            # Should be some text
            self.assertIsInstance(text, six.string_types, "Should be some text")

            # Should be non-empty for existing items
            self.assertGreater(len(text), 0, "Should be non-empty")

        # Should raise exception for invalid file items
        with self.assertRaises(Exception, msg="Should raise exception for invalid file items"):
            text = self.loader.getTextFor({})

    def test_getTextForName(self):
        testableNames = [
            ('test-rq', qType['SPARQL']),
            ('test-sparql', qType['SPARQL']),
            ('test-tpf', qType['TPF'])
        ]
        for name, expectedType in testableNames:
            text, actualType = self.loader.getTextForName(name)
            self.assertEqual(expectedType, actualType, "Query type should match %s != %s" % (expectedType, actualType))


class TestLocalLoader(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.loader = LocalLoader(path.join('tests', 'repo'))

    def test_fetchFiles(self):
        files = self.loader.fetchFiles()

        # Should return a list of file items
        self.assertIsInstance(files, list, "Should return a list of file items")

        # Should have N files (where N=9)
        self.assertEqual(len(files), 9, "Should return correct number of files")

        # File items should have a download_url
        for fItem in files:
            self.assertIn('download_url', fItem, "File items should have a download_url")

    def test_getRawRepoUri(self):
        repoUri = self.loader.getRawRepoUri()

        # Should be a string
        self.assertIsInstance(repoUri, six.string_types, "Should be a string")

        # For local repo, should be empty ?
        self.assertEqual(repoUri, "", "Should be an empty string")

    def test_getTextFor(self):
        files = self.loader.fetchFiles()

        # the contents of each file
        for fItem in files:
            text = self.loader.getTextFor(fItem)

            # Should be some text
            self.assertIsInstance(text, six.string_types, "Should be some text")

            # Should be non-empty for existing items
            self.assertGreater(len(text), 0, "Should be non-empty")

        # Should raise exception for invalid file items
        with self.assertRaises(Exception, msg="Should raise exception for invalid file items"):
            text = self.loader.getTextFor({})

    def test_getTextForName(self):
        testableNames = [
            ('test-rq', qType['SPARQL']),
            ('test-sparql', qType['SPARQL']),
            ('test-tpf', qType['TPF'])
        ]
        for name, expectedType in testableNames:
            text, actualType = self.loader.getTextForName(name)
            self.assertEqual(expectedType, actualType, "Query type should match %s != %s" % (expectedType, actualType))


class TestURLLoader(unittest.TestCase):
    @classmethod
    @patch('requests.get', side_effect=mock_requestsUrl)
    def setUpClass(self, x):
        self.specURL = 'http://example.org/url.yml'
        self.loader = URLLoader(self.specURL)
        print('Starting loader...')

    def test_fetchFiles(self):
        files = self.loader.fetchFiles()

        # Should return a list of file items
        self.assertIsInstance(files, list, "Should return a list of file items")

        # Should have N files (where N=3)
        self.assertEqual(len(files), 3, "Should return correct number of files")

        # File items should have a download_url
        for fItem in files:
            self.assertIn('download_url', fItem, "File items should have a download_url")

    def test_getRawRepoUri(self):
        repoUri = self.loader.getRawRepoUri()

        # Should be a string
        self.assertIsInstance(repoUri, six.string_types, "Should be a string")

        # Should be the same one we used to create the repo
        self.assertIn(self.specURL, repoUri, "Should be the same URL it was initialized with")

    @patch('requests.get', side_effect=mock_requestsUrl)
    def test_getTextFor(self, x):
        files = self.loader.fetchFiles()

        # the contents of each file
        for fItem in files:
            text = self.loader.getTextFor(fItem)

            # Should be some text
            self.assertIsInstance(text, six.string_types, "Should be some text")

            # Should be non-empty for existing items
            self.assertGreater(len(text), 0, "Should be non-empty")

        # Should raise exception for invalid file items
        with self.assertRaises(Exception, msg="Should raise exception for invalid file items"):
            text = self.loader.getTextFor({})

    def test_getTextForName(self):
        testableNames = [
            ('test-rq', qType['SPARQL']),
            ('test-sparql', qType['SPARQL']),
            ('test-tpf', qType['TPF'])
        ]
        for name, expectedType in testableNames:
            text, actualType = self.loader.getTextForName(name)
            self.assertEqual(expectedType, actualType, "Query type should match %s != %s" % (expectedType, actualType))


if __name__ == '__main__':
    unittest.main()
