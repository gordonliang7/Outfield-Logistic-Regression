import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from sklearn.linear_model import LinearRegression as LinReg, LogisticRegression as LogReg 
import matplotlib.pyplot as plt
import seaborn as sns
chrome_options = Options()
chrome_options.add_argument('--headless')

def extract(item, key):
    try:
        return item[key]
    except:
        return None

def circle_info(circle):
    classes = extract(circle,'class')
    return {'Out?': 'out' in classes,
           'Distance Covered': (int(extract(circle,'cx'))-.5)*140/500,
           'Hang Time': (int(extract(circle,'cy'))-400.5)*-8/400,
           'Wall?': 'wall' in classes,
           'Back?': 'back' in classes,
           'Out Binary': 1 if 'out' in classes else 0,
           'Wall Binary': 1 if 'wall' in classes else 0,
           'Back Binary': 1 if 'back' in classes else 0,
           'BBD': 'OUT' if 'out' in classes else 'HIT'}


def OFrange():
    URI = input('Paste Savant Link Here: ')
    driver = webdriver.Chrome(options = chrome_options)
    driver.get(URI)
    dropdownElement = driver.find_element(By.ID, "statcast-season-mlb")
    dropdown = Select(dropdownElement)
    soup = BeautifulSoup(driver.page_source,'html.parser')
    information = [circle_info(circle) for circle in soup.find(id = 'svg_LineChart').find_all('circle') if extract(circle,'class')]
    driver.quit()
    return pd.DataFrame(information)

def OFlogreg(df):
    '''Gives a dataframe with the structure from OFrange
    and return a Logistic Regression object based on
    Distance Covered and Hang Time'''
    logreg = LogReg(fit_intercept = True)
    logreg.fit(X = df[['Distance Covered', 'Hang Time']], y = df['Out Binary'])
    return logreg

def find50(lg):
    '''Give a logistic regression item from OFlogreg
    and get a function that takes in a distance covered
    and returns the hang time for catch probability to be
    50%'''
    coefs = lg.coef_[0]
    def givedist(x):
        return ((coefs[0]*x) + lg.intercept_[0])/(-coefs[1])
    return givedist

def lglink():
    return OFlogreg(OFrange())

def chartRange():
    df = OFrange()
    foo = find50(OFlogreg(df))
    plt.rcParams['figure.facecolor'] = 'white'
    xs = np.linspace(0,140,10000)
    ys = [foo(x) for x in xs]
    plt.plot([0,140],[foo(0),foo(140)])
    plt.xlim(0,140)
    plt.ylim(0,8)
    plt.xlabel('Distance From Ball Landing (ft)')
    plt.ylabel('Hang Time (seconds)')
    plt.fill_between(xs,ys,[8]*10000,color = 'green', label = 'Catch Prob > 50%', alpha = .3)
    plt.fill_between(xs,ys,color = 'red',label = 'Catch Prob < 50%', alpha = .3)
    sns.scatterplot(data = df, x = 'Distance Covered', y = 'Hang Time', style = 'BBD')
    plt.legend()