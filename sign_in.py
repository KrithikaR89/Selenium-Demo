from simple_setup import *
from simple_setup import simpleSetup as s
from load_and_search import loadAndSearch as las
from perf_analysis import perfAnalysis as p
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import logging
import datetime
import time

class signIn(simpleSetup):
    def __init__(self):
        super(signIn, self).__init__()

    def readSignIn(self, driver):
        """
        :param: driver instance
        :return: 
        """
        self.driver = driver
        
        l = las()
        config = l.readConfig()

        base_logger.info("Reading config file for user flow tests now...")
        
        self.user_link_assert = config['Search']['link_assert'].encode('ascii', 'ignore')
        self.user_search_link = config['SignIn']['load_link']
        self.user_signin_account = config['SignIn']['signin_account'].encode('ascii', 'ignore')
        self.user_signin_password = config['SignIn']['signin_password'].encode('ascii', 'ignore')

        return

    def logInPage(self):
        """
        :param: 
        :return: 
        """
        base_logger.info("Launching {0!s} now...".format(self.user_search_link))
        #self.driver.maximize_window()
        self.driver.get(self.user_search_link)
        
        if self.user_link_assert in self.driver.title:
            base_logger.info("Loaded {0!s} successfully".format(self.user_search_link))

            base_logger.info("Setting up hover action now...")
            
            test_elem = self.driver.find_element_by_id("nav-link-accountList")
            test_elem.location_once_scrolled_into_view
            time.sleep(2)

            elem_to_hover = self.driver.find_element_by_id("nav-link-accountList")
            hover = ActionChains(self.driver).move_to_element(elem_to_hover)
            hover.perform()
            time.sleep(5)

            try:
                wait = WebDriverWait(self.driver, 10)
                sg_elem = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="nav-flyout-ya-signin"]/a/span')))
                if sg_elem:
                    base_logger.info("Hover action worked as expected. Clicking on 'Sign In' now...")
                    sg_elem.click()

            except Exception as e:
                base_logger.error("Failed to locate 'Sign In' on webpage due to {0!s}".format(e))

            return

    def logIn(self, rerun=False):
        """
        :param:
        :return:None/metrics: List of recorded performance metrics
        """
        base_logger.info("Starting log in process with email {0!s}".format(self.user_signin_account))

        for wait in range(5):
            if "Amazon Sign-In" not in self.driver.title:
                time.sleep(3)
                base_logger.info("Waiting on page to load...")
            else:
                base_logger.info("Page has loaded!")
                break
        
        try:
            account_elem = self.driver.find_element_by_id('ap_email')
            time.sleep(2)
            
            base_logger.info("Found the element!")
            
            account_elem.clear()
            time.sleep(2)
            
            base_logger.info("Entering account address...")
            account_elem.send_keys(self.user_signin_account)
            time.sleep(3)
            continue_elem = self.driver.find_element_by_id("continue").click()
            time.sleep(3)
            
            password_elem = self.driver.find_element_by_id("ap_password")
            time.sleep(3)
            password_elem.clear()
            time.sleep(3)

            base_logger.info("Entering account password...")
            password_elem.send_keys(self.user_signin_password)
            time.sleep(3)

            signin_elem = self.driver.find_element_by_id("signInSubmit").click()
            if not rerun:
                metrics = self.callMetrics()
            time.sleep(10)

            phone_elem = self.driver.find_element_by_id("ap-account-fixup-phone-skip-link")
            if phone_elem:
                phone.click()
            
        except Exception as e:
            base_logger.error("Sign in process encountered following error : {0!s}".format(e))

        if not rerun:
            return metrics
        return None

    def callMetrics(self):
        """
        :param:
        :return:metric: List of recorded performance metrics
        """
        base_logger.info("Recording performance metrics now...")
        
        perf = p()

        metrics = perf.calcStatsLAS(self.driver)

        return metrics

    def verifySignIn(self):
        """
        :param:
        :return:login_success : Bool representing success or failure of login verification
        """
        base_logger.info("Verifying sign-in completion now...")
        login_success = False

        elem = self.driver.find_element_by_xpath('//*[@id="nav-your-amazon-text"]/span').text

        target = elem.lower()

        if target in self.user_signin_account:
            base_logger.info("Signin successful!")
            login_success = True

        return login_success

    def signOut(self, browser, driver):
        """
        :param:
        :return:so_success: Bool representing success or failure of sign out
        """
        self.driver = driver
        so_success = False
        base_logger.info("Pulling up account menu now...")

        try:
            if browser != "Firefox":
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(2)
                
            element = self.driver.find_element_by_id("nav-link-accountList")
            hover = ActionChains(self.driver).move_to_element(element)
            hover.perform()

            time.sleep(3)

            base_logger.info("Clicking on sign out now...")
            so = self.driver.find_element_by_id('nav-item-signout')
            time.sleep(3)

            so.click()
            time.sleep(2)

            if self.driver.find_element_by_id("ap_email"):
                base_logger.info("Sign-out completed successfully!")
                so_success = True

        except Exception as e:
            base_logger.error("Sign out process encountered following error : {0!s}".format(e))

        return so_success






















