from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import os
import pandas as pd
from datetime import date
from datetime import datetime


class CCLIReporting:

    def __init__(self, dir_used_songs = 'usage_reports', dir_reported_songs = 'reported_songs', testmode = True):
        self.test = testmode
        self.wait = 10
        self.dir_used_songs = dir_used_songs
        self.dir_reported_songs = dir_reported_songs
        self.import_reported_songs()
        self.import_usage_reports()

    def import_usage_reports(self):
        files = os.listdir(self.dir_used_songs)
        usage_reports = [None] * len(files)
        for i in list(range(len(files))):
            usage_reports[i] = (
                pd.read_csv(
                    os.path.join(self.dir_used_songs, files[i]),
                    delimiter='|', 
                    usecols=['CCLI Number', 'Dates Used'],
                    dtype={'CCLI Number': 'Int64', 'Dates Used': str}
                )
                .dropna(subset = 'CCLI Number')
            )
            usage_reports[i].columns = ['ccli_number', 'date_used']
            usage_reports[i]['date_used'] = usage_reports[i]['date_used'].str.split(
                "(?<=\d{4}),")
            usage_reports[i] = usage_reports[i].explode('date_used')
            
            months_translations = {'Mär': 'Mar', 'Mai': 'May', 'Okt': 'Oct', 'Dez': 'Dec'}
            usage_reports[i]['date_used'] = pd.to_datetime(
                usage_reports[i]['date_used'].replace(months_translations, regex=True)
            )
        
        if len(usage_reports) > 0:
            self.used_songs = (
                pd.concat(usage_reports)
                .drop_duplicates()
                .sort_values('date_used')
                .reindex(columns=['date_used', 'ccli_number'])
                .reset_index(drop=True)
            )
        else:
            self.used_songs = pd.DataFrame(
                columns=['date_used', 'ccli_number']
            )

    def import_reported_songs(self):
        files = os.listdir(self.dir_reported_songs)
        song_reports = [None] * len(files)
        for i in list(range(len(files))):
            song_reports[i] = pd.read_csv(
                os.path.join(self.dir_reported_songs, files[i]),
                delimiter='|',
                dtype={'ccli_number': 'Int64'},
                parse_dates=['date_used']
            )

        if len(song_reports) > 0:
            self.reported_songs = (
                pd.concat(song_reports)
                .drop_duplicates()
                .dropna()
                .sort_values('date_used')
                .reset_index(drop=True)
            )
        else:
            self.reported_songs = pd.DataFrame(
                columns=['date_used', 'ccli_number', 'date_reported']
            )

    def report_songs(self, email, password):        
        merged = self.used_songs.merge(
            self.reported_songs,
             how='outer',
             on=['date_used', 'ccli_number'],
             indicator=True
        )

        to_report = (
            merged[merged._merge == 'left_only']
            .drop(columns = '_merge')
            # .groupby('ccli_number')
            # .count()
            .reset_index(drop=True)
        )

        if len(to_report) > 0:
            # CCLI login
            self.driver = webdriver.Firefox()
            self.driver.get('https://profile.ccli.com/account/signin')
            self.driver.find_element(By.ID, 'EmailAddress').send_keys(email)
            self.driver.find_element(By.ID, 'Password').send_keys(password)
            self.driver.find_element(By.ID, 'sign-in').click()

            to_report['success'] = to_report['ccli_number'].apply(self.report_song)

            newly_reported = (
                to_report[to_report.success == True]
                .drop(columns='success')
            )
            newly_reported['date_reported'] = date.today()#.strftime("%Y-%m-%d")

            newly_reported.to_csv(
                os.path.join(self.dir_reported_songs, 'reporting_' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '.csv'),
                sep='|',
                index=False
            )

            # self.reported_songs = self.reported_songs.concat(newly_reported)
            self.reported_songs = pd.concat([self.reported_songs, newly_reported])

            self.close()

    def report_song(self, id):
        wait = WebDriverWait(self.driver, self.wait)
        self.driver.implicitly_wait(self.wait)
        self.driver.get('https://reporting.ccli.com/search?s=' + str(id))
        
        button_meldung = self.driver.find_element(By.CSS_SELECTOR, 'button.small:nth-child(2)')
        wait.until(ec.element_to_be_clickable(button_meldung))
        button_meldung.click()
        
        try:
            field_digital = self.driver.find_element(By.ID, 'cclDigital')
            wait.until(ec.element_to_be_clickable(field_digital))
            field_digital.send_keys('1')


            if self.test == True:
                # click 'Abbrechen' if in test mode
                button_abbrechen = self.driver.find_element(By.CSS_SELECTOR, 'div.margin-top-2r:nth-child(3) > button:nth-child(1)')
                WebDriverWait(self.driver, self.wait).until(ec.element_to_be_clickable(button_abbrechen))
                button_abbrechen.click()
            else:
                # klick 'Speicher' if not in test mode
                button_speichern = self.driver.find_element(By.CSS_SELECTOR, 'div.margin-top-2r:nth-child(3) > button:nth-child(2)')
                WebDriverWait(self.driver, self.wait).until(ec.element_to_be_clickable(button_speichern))
                button_speichern.click()
            
            return True

        except:

            # also return True if the song is 'gemeinfrei'
            if self.driver.find_elements(By.CSS_SELECTOR, '.callout'):
                return True

            self.driver.find_element(
                By.CSS_SELECTOR, 'div.margin-top-2r:nth-child(3) > button:nth-child(1)').click()
            return False

    def close(self):
        self.driver.close()
