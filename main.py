import getpass
import ccli
from pandas.testing import assert_frame_equal
import importlib
importlib.reload(ccli)

email = ''

# report to CCLI
reporting = ccli.CCLIReporting(testmode=False)

reporting.report_songs(email, getpass.getpass())

cols = ['ccli_number', 'date_used']
assert_frame_equal(
    reporting.used_songs.sort_values(by=cols).reset_index(drop=True),
    reporting.reported_songs.get(['date_used', 'ccli_number']).sort_values(
        by=cols).reset_index(drop=True)
)

reporting.import_usage_reports()
reporting.used_songs.query('ccli_number == 7051762')
reporting.reported_songs.query('ccli_number == 7051762')
reversed(cols)