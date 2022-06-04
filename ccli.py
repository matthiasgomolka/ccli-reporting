from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import os
import pandas as pd

class CCLIReporting:

    def __init__(self, email, password):
        self.test = True
        self.wait = 5
        self.reported = []
        self.driver = webdriver.Firefox()

        self.driver.get('https://profile.ccli.com/account/signin')
        self.driver.find_element(By.ID, 'EmailAddress').send_keys(email)
        self.driver.find_element(By.ID, 'Password').send_keys(password)
        self.driver.find_element(By.ID, 'sign-in').click()
        self.driver.get('https://reporting.ccli.com/search')
        WebDriverWait(self.driver, self.wait).until(
            ec.element_to_be_clickable((By.ID, 'SearchIinput')))

    def import_usage_reports(self, dir_reports = 'usage_reports'):
        files = os.listdir(dir_reports)
        usage_reports = [None] * len(files)
        for i in list(range(len(files))):
            usage_reports[i] = pd.read_csv(
                    os.path.join(dir_reports, files[i]), 
                    delimiter='|', 
                    dtype={'Name': str, 'Artist': str, 'CCLI Number': 'Int64', 'Dates Used': str}
                )
            usage_reports[i]['Dates Used'] = usage_reports[i]['Dates Used'].str.split("(?<=\d{4}),")
            usage_reports[i] = usage_reports[i].explode('Dates Used')
            
            months_translations = {'Mär': 'Mar', 'Mai': 'May', 'Okt': 'Oct', 'Dez': 'Dec'}
            usage_reports[i]['Dates Used'] = pd.to_datetime(
                usage_reports[i]['Dates Used'].replace(months_translations, regex = True)
            )
            
        self.usage = (
            pd.concat(usage_reports)
            .drop_duplicates()
            .dropna()
            .reset_index(drop=True)
        )

        
        # .groupby('CCLI Number')
        # .size()

    def report_song(self, id):
        self.driver.find_element(By.ID, 'SearchIinput').clear()
        self.driver.find_element(By.ID, 'SearchIinput').send_keys(id)
        self.driver.find_element(By.ID, 'SearchIinput').send_keys(Keys.ENTER)
        
        #time.sleep(5)
        
        WebDriverWait(self.driver, self.wait).until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, 'button.small:nth-child(2)')))
        self.driver.find_element(
            By.CSS_SELECTOR, 'button.small:nth-child(2)').click()
        
        try:
            WebDriverWait(self.driver, self.wait).until(
                ec.element_to_be_clickable((By.ID, 'cclDigital')))
            self.driver.find_element(By.ID, 'cclDigital').send_keys('1')

            if self.test == True:
                WebDriverWait(self.driver, self.wait).until(
                    ec.element_to_be_clickable((By.CSS_SELECTOR, 'div.margin-top-2r:nth-child(3) > button:nth-child(1)')))
                self.driver.find_element(
                    By.CSS_SELECTOR, 'div.margin-top-2r:nth-child(3) > button:nth-child(1)').click()
            else:
                WebDriverWait(self.driver, self.wait).until(
                    ec.element_to_be_clickable((By.CSS_SELECTOR, 'div.margin-top-2r:nth-child(3) > button:nth-child(2)')))
                self.driver.find_element(
                    By.CSS_SELECTOR, 'div.margin-top-2r:nth-child(3) > button:nth-child(2)').click()
            

        except:
            self.driver.find_element(
                By.CSS_SELECTOR, 'div.margin-top-2r:nth-child(3) > button:nth-child(1)').click()

        
        return id

    def close(self):
        self.driver.close()
