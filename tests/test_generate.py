from aclpub2.generate import get_conference_dates
import yaml


def test_get_conference_dates():
    conference = yaml.safe_load(
        """
start_date: 2025-03-04
end_date: 2025-03-05
    """
    )
    assert get_conference_dates(conference) == "March 4"

    conference = yaml.safe_load(
        """
start_date: 2025-03-04
end_date: 2025-03-05
    """
    )
    assert get_conference_dates(conference) == "March 4-5"

    conference = yaml.safe_load(
        """
start_date: 2025-03-04
end_date: 2025-03-05
    """
    )
    assert get_conference_dates(conference) == "March 3 - March 4"
