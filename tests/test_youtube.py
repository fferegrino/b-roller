import pytest

from b_roller.youtube import get_video_id, to_hh_mm_ss


@pytest.mark.parametrize(
    ["url", "expected_video_id"],
    [
        ("google.com", None),
        ("https://youtu.be/e7e9rVKCZyI", "e7e9rVKCZyI"),
        ("https://www.youtube.com/watch?v=e7e9rVKCZyI", "e7e9rVKCZyI"),
        ("https://www.youtube.com/watch?v=e7e9rVKCZyI&t=1", "e7e9rVKCZyI"),
        ("https://youtu.be/e7e9rVKCZyI?t=1", "e7e9rVKCZyI"),
        ("https://www.youtube.com/clip/UgkxW_Pm9YwQpCE0uXzRO1wmuAFZ9UgJk_ir", None),
    ],
)
def test_get_video_id(url, expected_video_id):
    actual_get_video_id = get_video_id(url)
    assert actual_get_video_id == expected_video_id


@pytest.mark.parametrize(
    ["input_time", "expected_time"],
    [
        ("123", "00:02:03"),
        ("1234", "00:20:34"),
        ("12345", "03:25:45"),
        ("13:55", "00:13:55"),
        ("00:13:55", "00:13:55"),
        (None, None),
    ],
)
def test_to_hh_mm_ss(input_time, expected_time):
    actual = to_hh_mm_ss(input_time)
    assert actual == expected_time
