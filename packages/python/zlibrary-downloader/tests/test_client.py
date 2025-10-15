"""
Unit tests for zlibrary_downloader.client module.

Tests cover the Zlibrary API client class, including:
- Client initialization
- Login functionality (email/password and auth token)
- Book search with various parameters
- Book download functionality
- Error handling and edge cases

Target: >80% code coverage
"""

from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from zlibrary_downloader.client import Zlibrary


class TestZlibraryClient:
    """Test suite for Zlibrary API client class."""

    @patch("zlibrary_downloader.client.requests.post")
    def test_client_initialization_no_credentials(self, mock_post: Mock) -> None:
        """Test that Zlibrary client initializes without credentials."""
        client = Zlibrary()
        assert not client.isLoggedIn()
        mock_post.assert_not_called()

    @patch("zlibrary_downloader.client.requests.post")
    def test_client_initialization_with_email_password(
        self, mock_post: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test that Zlibrary client initializes and logs in with email/password."""
        mock_response = Mock()
        mock_response.json.return_value = sample_login_response
        mock_post.return_value = mock_response

        client = Zlibrary(email="test@example.com", password="testpass")

        assert client.isLoggedIn()
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "test@example.com" in str(call_args)
        assert "testpass" in str(call_args)

    @patch("zlibrary_downloader.client.requests.get")
    def test_client_initialization_with_token(
        self, mock_get: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test that Zlibrary client initializes with auth token."""
        mock_response = Mock()
        mock_response.json.return_value = sample_login_response
        mock_get.return_value = mock_response

        client = Zlibrary(remix_userid="123456", remix_userkey="test_key")

        assert client.isLoggedIn()
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "123456" in str(call_args)
        assert "test_key" in str(call_args)

    @patch("zlibrary_downloader.client.requests.post")
    def test_login_with_email_password(
        self, mock_post: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test login using email and password credentials."""
        mock_response = Mock()
        mock_response.json.return_value = sample_login_response
        mock_post.return_value = mock_response

        client = Zlibrary()
        result = client.login("test@example.com", "testpass")

        assert result["success"] is True
        assert client.isLoggedIn()
        assert "user" in result

    @patch("zlibrary_downloader.client.requests.get")
    def test_login_with_auth_token(
        self, mock_get: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test login using authentication token."""
        mock_response = Mock()
        mock_response.json.return_value = sample_login_response
        mock_get.return_value = mock_response

        client = Zlibrary()
        result = client.loginWithToken("123456", "test_key")

        assert result["success"] is True
        assert client.isLoggedIn()

    @patch("zlibrary_downloader.client.requests.post")
    def test_login_failure(self, mock_post: Mock) -> None:
        """Test login failure handling."""
        mock_response = Mock()
        mock_response.json.return_value = {"success": False, "error": "Invalid credentials"}
        mock_post.return_value = mock_response

        client = Zlibrary()
        result = client.login("invalid@example.com", "wrongpass")

        assert result["success"] is False
        assert not client.isLoggedIn()

    @patch("zlibrary_downloader.client.requests.post")
    def test_search_books(
        self, mock_post: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test book search functionality."""
        # Mock login
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response

        # Mock search
        mock_search_response = Mock()
        search_results = {
            "success": True,
            "books": [
                {"id": "1", "title": "Book 1"},
                {"id": "2", "title": "Book 2"},
            ],
        }
        mock_search_response.json.return_value = search_results

        mock_post.side_effect = [mock_login_response, mock_search_response]

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.search(message="python programming")

        assert result == search_results
        assert mock_post.call_count == 2

    @patch("zlibrary_downloader.client.requests.post")
    def test_search_with_filters(
        self, mock_post: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test book search with various filters (language, format, year)."""
        # Mock login
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response

        # Mock search
        mock_search_response = Mock()
        search_results = {"success": True, "books": []}
        mock_search_response.json.return_value = search_results

        mock_post.side_effect = [mock_login_response, mock_search_response]

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.search(
            message="python",
            yearFrom=2020,
            yearTo=2024,
            languages="english",
            extensions="pdf",
            page=1,
            limit=10,
        )

        assert result == search_results
        # Verify search was called with filters
        search_call = mock_post.call_args_list[1]
        assert "python" in str(search_call)

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_download_book(
        self,
        mock_post: Mock,
        mock_get: Mock,
        sample_login_response: Dict[str, Any],
        sample_book_data: Dict[str, Any],
        sample_book_file_response: Dict[str, Any],
    ) -> None:
        """Test book download functionality."""
        # Mock login
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        # Mock file metadata request
        mock_file_response = Mock()
        mock_file_response.json.return_value = sample_book_file_response

        # Mock file download request
        mock_download_response = Mock()
        mock_download_response.status_code = 200
        mock_download_response.content = b"PDF content here"

        mock_get.side_effect = [mock_file_response, mock_download_response]

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.downloadBook(sample_book_data)

        assert result is not None
        filename, content = result
        assert filename.endswith(".pdf")
        assert content == b"PDF content here"
        assert "Test Book" in filename

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_download_book_failure(
        self,
        mock_post: Mock,
        mock_get: Mock,
        sample_login_response: Dict[str, Any],
        sample_book_data: Dict[str, Any],
        sample_book_file_response: Dict[str, Any],
    ) -> None:
        """Test download failure handling."""
        # Mock login
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        # Mock file metadata request
        mock_file_response = Mock()
        mock_file_response.json.return_value = sample_book_file_response

        # Mock file download request with failure
        mock_download_response = Mock()
        mock_download_response.status_code = 404

        mock_get.side_effect = [mock_file_response, mock_download_response]

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.downloadBook(sample_book_data)

        assert result is None

    @patch("zlibrary_downloader.client.requests.post")
    def test_http_request_error_handling(self, mock_post: Mock) -> None:
        """Test HTTP request error handling."""
        mock_post.side_effect = Exception("Network error")

        client = Zlibrary()

        with pytest.raises(Exception, match="Network error"):
            client.login("test@example.com", "testpass")

    @patch("zlibrary_downloader.client.requests.post")
    def test_search_without_login(
        self, mock_post: Mock, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that search requires login."""
        client = Zlibrary()
        result = client.search(message="test")

        # Should return empty dict when not logged in
        assert result == {}
        # Should print "Not logged in" message
        captured = capsys.readouterr()
        assert "Not logged in" in captured.out

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_get_profile(
        self,
        mock_post: Mock,
        mock_get: Mock,
        sample_login_response: Dict[str, Any],
        sample_profile_response: Dict[str, Any],
    ) -> None:
        """Test getting user profile."""
        # Mock login
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        # Mock profile request
        mock_profile_resp = Mock()
        mock_profile_resp.json.return_value = sample_profile_response
        mock_get.return_value = mock_profile_resp

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.getProfile()

        assert result == sample_profile_response
        assert result["user"]["email"] == "test@example.com"

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_get_downloads_left(
        self,
        mock_post: Mock,
        mock_get: Mock,
        sample_login_response: Dict[str, Any],
        sample_profile_response: Dict[str, Any],
    ) -> None:
        """Test getting remaining downloads."""
        # Mock login
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        # Mock profile request
        mock_profile_resp = Mock()
        mock_profile_resp.json.return_value = sample_profile_response
        mock_get.return_value = mock_profile_resp

        client = Zlibrary(email="test@example.com", password="testpass")
        downloads_left = client.getDownloadsLeft()

        # downloads_limit (10) - downloads_today (3) = 7
        assert downloads_left == 7

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_get_image(
        self,
        mock_post: Mock,
        mock_get: Mock,
        sample_login_response: Dict[str, Any],
        sample_book_data: Dict[str, Any],
    ) -> None:
        """Test getting book cover image."""
        # Mock login
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        # Mock image request
        mock_image_response = Mock()
        mock_image_response.status_code = 200
        mock_image_response.content = b"image data"
        mock_get.return_value = mock_image_response

        client = Zlibrary(email="test@example.com", password="testpass")
        image_data = client.getImage(sample_book_data)

        assert image_data == b"image data"

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_get_image_failure(
        self,
        mock_post: Mock,
        mock_get: Mock,
        sample_login_response: Dict[str, Any],
        sample_book_data: Dict[str, Any],
    ) -> None:
        """Test getting book cover image when request fails."""
        # Mock login
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        # Mock image request with failure
        mock_image_response = Mock()
        mock_image_response.status_code = 404
        mock_get.return_value = mock_image_response

        client = Zlibrary(email="test@example.com", password="testpass")
        image_data = client.getImage(sample_book_data)

        assert image_data is None

    @patch("zlibrary_downloader.client.requests.post")
    def test_update_info(
        self, mock_post: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test updating user information."""
        # Mock login
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response

        # Mock update request
        mock_update_response = Mock()
        update_result = {"success": True, "message": "Profile updated"}
        mock_update_response.json.return_value = update_result

        mock_post.side_effect = [mock_login_response, mock_update_response]

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.updateInfo(name="New Name", kindle_email="new@kindle.com")

        assert result == update_result
        assert result["success"] is True

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_get_most_popular(
        self, mock_post: Mock, mock_get: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test getting most popular books."""
        # Mock login
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        # Mock popular books request
        mock_popular_response = Mock()
        popular_books = {"success": True, "books": [{"id": "1", "title": "Popular Book"}]}
        mock_popular_response.json.return_value = popular_books
        mock_get.return_value = mock_popular_response

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.getMostPopular()

        assert result == popular_books

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_get_user_downloaded(
        self, mock_post: Mock, mock_get: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test getting user downloaded books."""
        # Mock login
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        # Mock downloaded books request
        mock_downloaded_response = Mock()
        downloaded_books = {"success": True, "books": []}
        mock_downloaded_response.json.return_value = downloaded_books
        mock_get.return_value = mock_downloaded_response

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.getUserDownloaded(order="year", page=1, limit=10)

        assert result == downloaded_books

    @patch("zlibrary_downloader.client.requests.post")
    def test_make_registration(self, mock_post: Mock) -> None:
        """Test user registration."""
        mock_response = Mock()
        registration_result = {"success": True, "message": "Registration successful"}
        mock_response.json.return_value = registration_result
        mock_post.return_value = mock_response

        client = Zlibrary()
        result = client.makeRegistration("new@example.com", "password123", "New User")

        assert result == registration_result
        assert result["success"] is True

    @patch("zlibrary_downloader.client.requests.post")
    def test_recover_password(self, mock_post: Mock) -> None:
        """Test password recovery."""
        mock_response = Mock()
        recovery_result = {"success": True, "message": "Recovery email sent"}
        mock_response.json.return_value = recovery_result
        mock_post.return_value = mock_response

        client = Zlibrary()
        result = client.recoverPassword("test@example.com")

        assert result == recovery_result
        assert result["success"] is True

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_save_book(
        self, mock_post: Mock, mock_get: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test saving a book."""
        # Mock login
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        # Mock save book request
        mock_save_response = Mock()
        save_result = {"success": True, "message": "Book saved"}
        mock_save_response.json.return_value = save_result
        mock_get.return_value = mock_save_response

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.saveBook("12345")

        assert result == save_result
        assert result["success"] is True

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_get_recently(
        self, mock_post: Mock, mock_get: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test getting recently added books."""
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        mock_recently_response = Mock()
        recently_books = {"success": True, "books": []}
        mock_recently_response.json.return_value = recently_books
        mock_get.return_value = mock_recently_response

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.getRecently()

        assert result == recently_books

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_get_user_recommended(
        self, mock_post: Mock, mock_get: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test getting user recommended books."""
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        mock_recommended_response = Mock()
        recommended_books = {"success": True, "books": []}
        mock_recommended_response.json.return_value = recommended_books
        mock_get.return_value = mock_recommended_response

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.getUserRecommended()

        assert result == recommended_books

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_delete_user_book(
        self, mock_post: Mock, mock_get: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test deleting a user book."""
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        mock_delete_response = Mock()
        delete_result = {"success": True}
        mock_delete_response.json.return_value = delete_result
        mock_get.return_value = mock_delete_response

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.deleteUserBook("12345")

        assert result == delete_result

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_unsave_user_book(
        self, mock_post: Mock, mock_get: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test unsaving a user book."""
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        mock_unsave_response = Mock()
        unsave_result = {"success": True}
        mock_unsave_response.json.return_value = unsave_result
        mock_get.return_value = mock_unsave_response

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.unsaveUserBook("12345")

        assert result == unsave_result

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_get_book_format(
        self, mock_post: Mock, mock_get: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test getting book formats."""
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        mock_format_response = Mock()
        format_result = {"success": True, "formats": ["pdf", "epub"]}
        mock_format_response.json.return_value = format_result
        mock_get.return_value = mock_format_response

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.getBookForamt("12345", "hash123")

        assert result == format_result

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_get_donations(
        self, mock_post: Mock, mock_get: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test getting user donations."""
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        mock_donations_response = Mock()
        donations_result = {"success": True, "donations": []}
        mock_donations_response.json.return_value = donations_result
        mock_get.return_value = mock_donations_response

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.getDonations()

        assert result == donations_result

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_get_extensions(
        self, mock_post: Mock, mock_get: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test getting available extensions."""
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        mock_extensions_response = Mock()
        extensions_result = {"success": True, "extensions": ["pdf", "epub"]}
        mock_extensions_response.json.return_value = extensions_result
        mock_get.return_value = mock_extensions_response

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.getExtensions()

        assert result == extensions_result

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_get_domains(
        self, mock_post: Mock, mock_get: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test getting available domains."""
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        mock_domains_response = Mock()
        domains_result = {"success": True, "domains": ["1lib.sk"]}
        mock_domains_response.json.return_value = domains_result
        mock_get.return_value = mock_domains_response

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.getDomains()

        assert result == domains_result

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_get_languages(
        self, mock_post: Mock, mock_get: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test getting available languages."""
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        mock_languages_response = Mock()
        languages_result = {"success": True, "languages": ["english", "spanish"]}
        mock_languages_response.json.return_value = languages_result
        mock_get.return_value = mock_languages_response

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.getLanguages()

        assert result == languages_result

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_get_plans(
        self, mock_post: Mock, mock_get: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test getting available plans."""
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        mock_plans_response = Mock()
        plans_result = {"success": True, "plans": []}
        mock_plans_response.json.return_value = plans_result
        mock_get.return_value = mock_plans_response

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.getPlans()

        assert result == plans_result

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_get_plans_with_language(
        self, mock_post: Mock, mock_get: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test getting plans with language switch."""
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        mock_plans_response = Mock()
        plans_result = {"success": True, "plans": []}
        mock_plans_response.json.return_value = plans_result
        mock_get.return_value = mock_plans_response

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.getPlans(switch_language="es")

        assert result == plans_result

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_get_user_saved(
        self, mock_post: Mock, mock_get: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test getting user saved books."""
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        mock_saved_response = Mock()
        saved_books = {"success": True, "books": []}
        mock_saved_response.json.return_value = saved_books
        mock_get.return_value = mock_saved_response

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.getUserSaved()

        assert result == saved_books

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_get_info(
        self, mock_post: Mock, mock_get: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test getting info."""
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        mock_info_response = Mock()
        info_result = {"success": True, "info": {}}
        mock_info_response.json.return_value = info_result
        mock_get.return_value = mock_info_response

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.getInfo()

        assert result == info_result

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_hide_banner(
        self, mock_post: Mock, mock_get: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test hiding banner."""
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        mock_hide_response = Mock()
        hide_result = {"success": True}
        mock_hide_response.json.return_value = hide_result
        mock_get.return_value = mock_hide_response

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.hideBanner()

        assert result == hide_result

    @patch("zlibrary_downloader.client.requests.post")
    def test_resend_confirmation(
        self, mock_post: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test resending confirmation email."""
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response

        mock_resend_response = Mock()
        resend_result = {"success": True}
        mock_resend_response.json.return_value = resend_result

        mock_post.side_effect = [mock_login_response, mock_resend_response]

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.resendConfirmation()

        assert result == resend_result

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_send_to(
        self, mock_post: Mock, mock_get: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test sending book to device."""
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        mock_sendto_response = Mock()
        sendto_result = {"success": True}
        mock_sendto_response.json.return_value = sendto_result
        mock_get.return_value = mock_sendto_response

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.sendTo("12345", "hash123", "kindle")

        assert result == sendto_result

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_get_book_info(
        self, mock_post: Mock, mock_get: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test getting book info."""
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        mock_bookinfo_response = Mock()
        bookinfo_result = {"success": True, "book": {}}
        mock_bookinfo_response.json.return_value = bookinfo_result
        mock_get.return_value = mock_bookinfo_response

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.getBookInfo("12345", "hash123")

        assert result == bookinfo_result

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_get_similar(
        self, mock_post: Mock, mock_get: Mock, sample_login_response: Dict[str, Any]
    ) -> None:
        """Test getting similar books."""
        mock_login_response = Mock()
        mock_login_response.json.return_value = sample_login_response
        mock_post.return_value = mock_login_response

        mock_similar_response = Mock()
        similar_result = {"success": True, "books": []}
        mock_similar_response.json.return_value = similar_result
        mock_get.return_value = mock_similar_response

        client = Zlibrary(email="test@example.com", password="testpass")
        result = client.getSimilar("12345", "hash123")

        assert result == similar_result

    @patch("zlibrary_downloader.client.requests.post")
    def test_make_token_signin(self, mock_post: Mock) -> None:
        """Test token sign-in."""
        mock_response = Mock()
        signin_result = {"success": True}
        mock_response.json.return_value = signin_result
        mock_post.return_value = mock_response

        client = Zlibrary()
        result = client.makeTokenSigin("Test User", "token123")

        assert result == signin_result

    @patch("zlibrary_downloader.client.requests.get")
    @patch("zlibrary_downloader.client.requests.post")
    def test_get_request_without_login(
        self, mock_post: Mock, mock_get: Mock, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test GET request without login."""
        client = Zlibrary()
        result = client.getProfile()

        assert result == {}
        captured = capsys.readouterr()
        assert "Not logged in" in captured.out

    @patch("zlibrary_downloader.client.requests.post")
    def test_send_code(self, mock_post: Mock) -> None:
        """Test sending verification code."""
        mock_response = Mock()
        send_result = {"success": True}
        mock_response.json.return_value = send_result
        mock_post.return_value = mock_response

        client = Zlibrary()
        result = client.sendCode("test@example.com", "password", "Test User")

        assert result["success"] is True
        assert "msg" in result

    @patch("zlibrary_downloader.client.requests.post")
    def test_send_code_failure(self, mock_post: Mock) -> None:
        """Test sending verification code failure."""
        mock_response = Mock()
        send_result = {"success": False, "error": "Failed"}
        mock_response.json.return_value = send_result
        mock_post.return_value = mock_response

        client = Zlibrary()
        result = client.sendCode("test@example.com", "password", "Test User")

        assert result["success"] is False
        assert "msg" not in result

    @patch("zlibrary_downloader.client.requests.post")
    def test_verify_code(self, mock_post: Mock) -> None:
        """Test verifying registration code."""
        mock_response = Mock()
        verify_result = {"success": True}
        mock_response.json.return_value = verify_result
        mock_post.return_value = mock_response

        client = Zlibrary()
        result = client.verifyCode("test@example.com", "password", "Test User", "123456")

        assert result == verify_result
