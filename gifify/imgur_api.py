"""Imgur API."""

from datetime import datetime
from datetime import timezone
from os import environ

import requests

START_DATE = datetime(2022, 1, 1, 0, 0, 0, 0, timezone.utc)
# End date currently unknown, will be updated
END_DATE = datetime(2023, 1, 1, 0, 0, 0, 0, timezone.utc)

def fetch_all_image_links():
    """Fetch list of all image links."""
    page_num = 0
    images = []
    while (True):
        data = fetch_user_submissions_page(page_num)
        found_cutoff, image_sublist = build_image_link_list(data)
        images.extend(image_sublist)
        if found_cutoff:
            break
        page_num += 1
    images.reverse()
    return images


def fetch_user_submissions_page(page_num=0):
    """Fetch user posts."""
    client_id = environ.get('IMGUR_CLIENT_ID')
    assert client_id, 'IMGUR_CLIENT_ID env var not set'
    print(f'API: Fetching page {page_num}')
    r = requests.get(
        f'https://api.imgur.com/3/account/GrateArtiste/submissions/{page_num}',
        headers={
            'Authorization': f'Client-ID {client_id}'
        }
    )
    return format_response(r)


def format_response(response):
    """Format Response."""
    assert response.status_code == 200, response.text
    result = response.json()
    assert 'data' in result, 'expected response to contain "data" key'
    assert result['data']
    return result['data']


def build_image_link_list(data):
    found_cutoff = False
    images = []
    for submission in data:
        validate_submission(submission)
        date_check = check_date_range(submission['datetime'])
        if date_check == 'after':
            continue
        elif date_check == 'before':
            found_cutoff = True
            break
        image_link = get_image_link(submission)
        if image_link not in images:
            images.append(image_link)
    return found_cutoff, images


def get_image_link(submission):
    """Get image link."""
    if submission['is_album']:
        return submission['images'][0]['link']
    return submission['link']


def check_date_range(submission_date):
    """Check cutoff date."""
    date = datetime.fromtimestamp(submission_date, timezone.utc)
    if date < START_DATE:
        return 'before'
    if date > END_DATE:
        return 'after'
    return 'within'



def validate_submission(submission):
    """Validate."""
    assert 'id' in submission
    assert 'datetime' in submission
    assert 'is_album' in submission
    assert 'link' in submission
    if submission['is_album']:
        assert 'images' in submission
        assert len(submission['images']) == 1
