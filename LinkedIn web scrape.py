# Import packages/functions
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import numpy as np
import lxml
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

import nltk
import pandas as pd
from nltk import word_tokenize, FreqDist
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
nltk.download
nltk.download('wordnet')
nltk.download('stopwords')
from nltk.tokenize import TweetTokenizer
from collections import Counter
import requests
import re
import string

from selenium.webdriver.common.keys import Keys

# Define functions to clean text (remove stop words, spaces, etc.)
def preprocess(text):
    text = text.lower() 
    text=text.strip()  
    text=re.compile('<.*?>').sub('', text) 
    text = re.compile('[%s]' % re.escape(string.punctuation)).sub(' ', text)  
    text = re.sub('\s+', ' ', text)  
    text = re.sub(r'\[[0-9]*\]',' ',text) 
    text=re.sub(r'[^\w\s]', '', str(text).lower().strip())
    text = re.sub(r'\d',' ',text) 
    text = re.sub(r'\s+',' ',text) 
    return text

def stopword(string):
    a= [i for i in string.split() if i not in stopwords.words('english')]
    return ' '.join(a)

def finalpreprocess(string):
    return stopword(preprocess(string))

def findtopwords(text):
    counts = Counter(re.findall('\w+', text))
    return counts.most_common()[0:5]

# Build up driver
driver = webdriver.Chrome()

email = "your account
password = "your password"

# Go to linkedin and login
driver.get('https://www.linkedin.com/login')
time.sleep(1)

driver.find_element('id', 'username').send_keys(email)
driver.find_element('id', 'password').send_keys(password)
driver.find_element('id', 'password').send_keys(Keys.RETURN)

# Define URL
'''As of March 1, 2023:
f_I=6%2C97%2C28%2C43%2C3132%2C4%2C96%2C80 defines industry (mainly focus on tech, market research, IT)
f_TPR=r604800 defines job posted time (this will filter out jobs that were posted in past week)
f_SB2=5 defines salary (this will filter out salary >= 120k)
'''

url = 'https://www.linkedin.com/jobs/search/?f_I=6%2C97%2C28%2C43%2C3132%2C4%2C96%2C80&f_TPR=r604800&f_SB2=5&keywords=consumer%20insights%20manager&location=United%20States'

driver.get(url)
time.sleep(3)

# Web scrape through pages (1-5) and get info for each job posting
position_v = []
company_v = []
location_v = []
details_v = []
link_v = []
num_applicant_v = []
posted_days_v = []
job_full_v = []
num_employee_v = []
skill_v = []
job_level_v = []
industry_v = []
salary_v = []

str1 = "[aria-label='Page "
str2 = "']"

for i in range(2,6):

    job_list = driver.find_elements(By.CLASS_NAME, "ember-view.jobs-search-results__list-item.occludable-update.p0.relative.scaffold-layout__list-item")    

    for job in job_list:
        # executes JavaScript to scroll the div into view
        driver.execute_script("arguments[0].scrollIntoView();", job)
        job.click()
        time.sleep(2)
        position = job.text.split('\n')[0]
        company = job.text.split('\n')[1]
        location = job.text.split('\n')[2]
        details = driver.find_element("id", "job-details").text
        link = driver.find_element(By.CLASS_NAME, 'disabled.ember-view.job-card-container__link.job-card-list__title').get_attribute('href')
        
        try:
            num_applicant = driver.find_element(By.CLASS_NAME, 'jobs-unified-top-card__applicant-count').text
        except:
            try: 
                num_applicant = driver.find_element(By.CLASS_NAME, 'jobs-unified-top-card__bullet').text
            except: 
                num_applicant = ''
                print('No applicant retrieved')
        
        try:
            posted_days = driver.find_element(By.CLASS_NAME, 'jobs-unified-top-card__posted-date').text
        except:
            posted_days = ''
        
        try:
            job_full = driver.find_element(By.CLASS_NAME, 'mt5.mb2').text.split('\n')[0] # Full time or part time, # of employees, skills
            num_employee = driver.find_element(By.CLASS_NAME, 'mt5.mb2').text.split('\n')[1] 
            skill = driver.find_element(By.CLASS_NAME, 'mt5.mb2').text.split('\n')[4] 
        except: 
            job_full = ''
            num_employee = ''
            skill = ''
        
        if re.search(' · ', job_full):
            job_full_tmp = job_full.split(' · ')[0]
            if any(chr.isdigit() for chr in job_full_tmp):
                salary = job_full_tmp
                job_full_tmp = job_full.split(' · ')[1]
                try:
                    job_level = job_full.split(' · ')[2]
                except:
                    job_level = ''
                job_full = job_full_tmp
            else:
                job_level = job_full.split(' · ')[1]
                job_full = job_full_tmp
                salary = ''
        else: 
            job_level = ''
            salary = ''
            
        
        if re.search(' · ', num_employee):
            num_employee_tmp = num_employee.split(' · ')[0]
            industry = num_employee.split(' · ')[1]
            num_employee = num_employee_tmp
        else: 
            industry = ''
        
        
        position_v.append(position)
        company_v.append(company)
        location_v.append(location)
        details_v.append(details)
        link_v.append(link)
        num_applicant_v.append(num_applicant)
        posted_days_v.append(posted_days)
        job_full_v.append(job_full)
        num_employee_v.append(num_employee)
        skill_v.append(skill)
        job_level_v.append(job_level)
        industry_v.append(industry)
        salary_v.append(salary)
        
    button_css = str1 + str(i) + str2
    driver.find_element(By.CSS_SELECTOR, button_css).click()
 
job_table = pd.DataFrame({'Position':position_v, 'Company':company_v, 'Location':location_v, 'Details':details_v, 'Link':link_v, '# of Applicants':num_applicant_v, 'Posted days':posted_days_v, 'Part/Full time':job_full_v, '# of Employees':num_employee_v, 'Skill':skill_v, 'Job level':job_level_v, 'Industry':industry_v, 'Salary':salary_v})

# Tockenize job descriptions and create word counts for each job posting
job_table['Details clean'] = job_table['Details'].apply(lambda x: finalpreprocess(x))
job_table['Details word counts'] = job_table['Details clean'].apply(lambda x: findtopwords(x))

# Create custom flags to find postings that are most related to our interestes (using customer insights, market research etc as keywords)
job_table['flag - consumer insights'] = job_table['Details clean'].str.contains('consumer insights', regex=False)
job_table['flag - market research'] = job_table['Details clean'].str.contains('market research', regex=False)
job_table['flag - syndicated'] = job_table['Details clean'].str.contains('syndicated', regex=False)
job_table['flag - segmentation'] = job_table['Details clean'].str.contains('segmentation', regex=False)
job_table['flag - brand insights'] = job_table['Details clean'].str.contains('brand insights', regex=False)
job_table['flag - customer insights'] = job_table['Details clean'].str.contains('customer insights', regex=False)
job_table['flag - brand strategy'] = job_table['Details clean'].str.contains('brand strategy', regex=False)

cols = ['flag - consumer insights', 'flag - market research', 'flag - syndicated', 'flag - segmentation', 'flag - brand insights', 'flag - customer insights', 'flag - brand strategy']
job_table['flag numbers'] = job_table[cols].sum(axis=1)


job_table = job_table.sort_values('flag numbers', ascending=False)
job_table.to_csv(r'your working directory/Job sheet.csv', index=False)

