import getpass
import ccli
from pandas.testing import assert_frame_equal
import importlib
importlib.reload(ccli)

email = ''

# report to CCLI
reporting = ccli.CCLIReporting()

reporting.report_songs(email, getpass.getpass())

assert_frame_equal(
    reporting.used_songs.sort_values(by=['ccli_number', 'date_used']).reset_index(drop=True), 
    reporting.reported_songs.sort_values(by=['ccli_number', 'date_used']).reset_index(drop=True)
)

