from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as c_Options
from selenium.webdriver.firefox.options import Options as f_Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import logging
import json
import time
import datetime
import os
import sys
import shutil
import pandas as pd

base_logger = logging.getLogger('Web Logger')
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(message)s\n', datefmt='%D %I:%M:%S %p')
time_stamp = datetime.datetime.now().strftime('%d-%m-%Y_%I-%M-%S%p')
file_name = 'web_testlog_{0!s}.log'.format(time_stamp)
f_handler = logging.FileHandler(file_name)
f_handler.setFormatter(formatter)
f_handler.setLevel(logging.INFO)
s_handler = logging.StreamHandler()
s_handler.setFormatter(formatter)
s_handler.setLevel(logging.INFO)
base_logger.addHandler(s_handler)
base_logger.addHandler(f_handler)
base_logger.setLevel(logging.INFO)
base_logger.propagate = False

class simpleSetup(object):
    def __init__(self):
        pass

    def _readConfig(self, path_to_file=None):
        """
        param:path_to_file (Optional) : Path to config file if outside CWD
        return:config : Dict containing relevant config values
        """
        base_logger.info("Reading Test Config File now...")
        
        if not path_to_file:
            path_to_file = os.getcwd()+'/'+'config.json'
        with open(path_to_file, 'r') as f:
            config = json.load(f)

        return config
        
    def initConfig(self, config):
        """
        param: config : Dict containing relevant config values
        return: None
        """

        base_logger.info("Here are the setup items...")
        
        self.browser = str(config['Setup']['browser'].encode('ascii', 'ignore'))
        base_logger.info("Requested browser is: {0!s}".format(self.browser))
        
        self.headless = str(config['Setup']['headless'].encode('ascii', 'ignore'))
        base_logger.info("Requested headless test mode is: {0!s}".format(self.headless))
        
        self.pagestg = str(config['Setup']['pageLoadStrategy'].encode('ascii', 'ignore'))
        base_logger.info("Requested page load is: {0!s}".format(self.pagestg))

        return self.browser, self.headless, self.pagestg

    def initDriver(self):
        """
        param:
        return:driver_load: Bool value representing outcome of driver load action
        return:wb_options: Dictionary carrying current browser capabilities
        """ 
        driver_load = True
        
        base_logger.info("Initializing WebDriver now...")
        
        if self.browser:
            try:
                base_logger.info("Initializing browser options for {0!s}".format(self.browser))
                driver = self.optionParser()
                self.driver = driver
            except Exception as e:
                base_logger.error("Tearing down. Failed to init driver due to {0!s}".format(e))
        else:
            driver_load = False
            base_logger.error("Unable to initialize driver, incorrect arguments passed!")

        return driver_load, driver
    
    def optionParser(self):
        """
        param:
        return: Webdriver instance
        """
        if self.browser=="Firefox" or self.browser=="firefox" or self.browser=="ff":
            options = f_Options()
            caps = DesiredCapabilities.FIREFOX.copy()
            if self.headless == "True":
                options.add_argument("--headless")
            if self.pagestg:
                caps['pageLoadStrategy'] = self.pagestg
            return webdriver.Firefox(firefox_options=options, desired_capabilities=caps)

        elif self.browser=="Chrome" or self.browser=="chrome":
            options = c_Options()
            caps = DesiredCapabilities().CHROME.copy()
            if self.headless == "True":
                options.add_argument("--headless")
            if self.pagestg:
                caps['pageLoadStrategy'] = self.pagestg
            return webdriver.Chrome(chrome_options=options, desired_capabilities=caps)

        elif self.browser=="Safari" or self.browser=="safari":
            driver = webdriver.Safari()
            driver.implicitly_wait(10)
            driver.maximize_window()
            return driver

        else:
            base_logger.error("Browser not specified as per format. Please refer to README.md")
            return None

    def teardown(self, special=False):
        """
        param:special (Optional): Needed when a testcase is run with multiple tabs open requiring a quit() rather than a close()
        return:
        """
        base_logger.info("Tearing down webdriver at {0!s}".format(datetime.datetime.now().strftime('%D %I:%M:%S %p')))
        if special:
            self.driver.quit()
        else:
            self.driver.close()
        time.sleep(5)
        base_logger.info("-----------------------------------------------")
        
        return

    def logpull(self):
        """
        param: test_type: String differentiating LAS vs UF runs
        return: csv_name : Name of final csv result file
        """
        csv_name=[]
        
        mv_list = []
        mv_list.append(file_name)

        if self.browser=="Firefox" or self.browser=="firefox" or self.browser=="ff":
            gck_path = 'geckodriver.log'
            if os.path.exists(gck_path):
                res_gck_path = gck_path+'_'+time_stamp+'.log'
                os.rename(gck_path, res_gck_path)
                mv_list.append(res_gck_path)
        
        all_files = os.listdir(os.getcwd())
        for new_file in all_files:
            if new_file.endswith('.csv'):
                df = pd.read_csv(new_file)
                df.reset_index(drop=True, inplace=True)
                df.drop('Unnamed: 0', axis=1, inplace=True)
                df.to_csv(new_file)
                mv_list.append(new_file)
                csv_name.append(new_file)
        
        res_path = os.getcwd()+'/'+'Logs'
        
        if not os.path.exists(res_path):
            base_logger.info("Result logs folder does not exist, creating folder now...")
            os.mkdir(res_path)

        base_logger.info("Creating a result directory for both test logs & browser logs...")
        tmp_res = self.browser+'_'+'Logs'+'_'+time_stamp
        os.mkdir(tmp_res)

        for new_file in mv_list:
            base_logger.info("Moving log file {0!s} to {1!s} folder".format(new_file, tmp_res))
            file_path = os.getcwd()+'/'+new_file
            
            try:
                shutil.move(file_path, tmp_res)
                full_path = tmp_res+'/'+new_file
                if os.path.exists(full_path):
                    base_logger.info("Log file has been moved successfully to tmp folder...")
            except Exception as e:
                base_logger.error("Tearing down. Failed to move results log due to {0!s}".format(e))

        base_logger.info("Temp folder {0!s} is now ready! Moving into final logs folder...".format(tmp_res))
        try:
            shutil.move(tmp_res, res_path)
            full_path = res_path+'/'+tmp_res
            if os.path.exists(full_path):
                base_logger.info("Log file has been moved successfully...")
        except Exception as e:
            base_logger.error("Tearing down. Failed to move results log due to {0!s}".format(e))

        return tmp_res, csv_name
 












