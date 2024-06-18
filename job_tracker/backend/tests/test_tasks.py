import requests

from ..tasks import generic_fetch_jobs

def test_generic_fetch_jobs(mocker):
    mock_get = mocker.patch('requests.get')

    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "data": [
            {
                "id": 1,
                "title": "Python Developer",
                "description": "Python, Flask, SQL",
                "location": "Mountain View, CA",
                "date_posted": "2021-01-01T00:00:00Z"
            }
        ],
        "message":"Success",
        "status":"success"
    }

    url = "http://example.com"
    result = generic_fetch_jobs(url)
    mock_get.assert_called_once_with(url, timeout=5)

    assert result[0] == True

    result = result[1]
    assert len(result) == 1
    assert result[0].title == "Python Developer"


def test_generic_fetch_jobs_timeout(mocker):
    mock_get = mocker.patch('requests.get')
    mock_get.side_effect = requests.exceptions.Timeout

    url = "http://example.com"
    result = generic_fetch_jobs(url)
    mock_get.assert_called_once_with(url, timeout=5)

    assert result[0] == False
    assert result[1] == "timeout"
