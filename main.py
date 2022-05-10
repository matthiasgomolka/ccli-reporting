import pandas as pd
import getpass
import ccli

email = ''

# get list of songs
ids = pd.read_csv(
    '/home/matthias/Downloads/Presenter Song Usage 2022-04-08 - 2022-05-08.csv', 
    usecols=['CCLI Number'],
    dtype={'CCLI Number': str}
).dropna().loc[:, 'CCLI Number'].tolist()

# report to CCLI
reporting = ccli.CCLIReporting(email, getpass.getpass())

reporting.reported_songs = [reporting.report_song(id) for id in ids]

reporting.close()
