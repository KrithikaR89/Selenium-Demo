from simple_setup import *
from simple_setup import simpleSetup as s
from load_and_search import loadAndSearch as las
from perf_analysis import perfAnalysis as p
from sign_in import signIn as si
from add_to_cart import addToCart as atc
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import logging
import os
import time
import datetime
import shutil

class country(simpleSetup):
    def __init__(self):
        super(country, self).__init__()

    def readCountry(self, driver):
        """
        :param:
        :return:
        """
        l = las()
        self.driver = driver
        
        country_config = l.readConfig()

        self.current_country = country_config['Country']['current_country'].encode('ascii', 'ignore')
        self.country = country_config['Country']['new_country'].encode('ascii', 'ignore')

        return

    def setFocus(self):
        """
        :param:
        :return: 
        """

        base_logger.info("Setting webpage focus to search box so as to dismiss hovers...")

        a_t_c = atc()
        
        a_t_c.readCart(self.driver)
        homepage = a_t_c.checkHomePage()
        
        if homepage:
            base_logger.info("Loaded homepage correctly, moving to textbox now")
            
            submit = self.driver.find_element_by_id('twotabsearchtextbox')
            time.sleep(1)
            submit.click()
            time.sleep(5)

        return

    def findCountry(self):
        """
        :param:
        :return:country_page: Bool representing success or failure of landing on country selection page
        """
        country_page = False

        try:
            flag = self.driver.find_element_by_id("icp-nav-flyout")
            time.sleep(3)
            
            base_logger.info("Hovering over Country icon now...")
            f_hover = ActionChains(self.driver).move_to_element(flag)
            f_hover.perform()
            time.sleep(5)
            
            base_logger.info("Starting country change now...")
            self.driver.find_element_by_id("icp-flyout-mkt-change").click()
            time.sleep(10)

        except Exception as e:
            base_logger.error("Failed to land on country selection page due to : {0!s}".format(e))

        if "Select your preferred country/region website:" in self.driver.page_source:
            base_logger.info("Landed on country selection page")
            country_page = True

        return country_page

    def selectIndex(self, country=None):
        """
        :param:country (Optional): Either None (new country) or current country (for cleanup)
        :return:country_found: Bool representing success or failure of finding requested country in available list
        :return:country_index : Str representing location of country in availability list
        """
        country_index = None
        country_found = False
        country_list = []

        if not country:
            country = self.country

        try:
            base_logger.info("Finding all available countries for selection...")
            country_op = Select(self.driver.find_element_by_id("icp-selected-country"))
            option = country_op.options

            for item in option:
                country_list.append(str(item.text.encode('ascii', 'ignore')).strip())

        except Exception as e:
            base_logger.error("Failed to find available countries due to : {0!s}".format(e))

        if country_list:
            country_list.pop(0)
            
            base_logger.info("Here are all the available selections : {0!s}".format(country_list))

            for i, v in enumerate(country_list):
                if v == country:
                    country_index = str(i)
                    base_logger.info("Requested country of {0!s} is available to select at index {1!s}".format(country, country_index))
                    country_found = True

        return country_found, country_index

    def chooseCountry(self, index, country=None):
        """
        :param:index: Position of requested country in availability list
        :param:country (Optional): Either None (new country) or current country (for cleanup)
        :return:metrics: Perf metrics for country switch
        """
        if not country:
            country = self.country

        base_logger.info("Choosing {0!s} now...".format(country))
        
        country_dropdown = self.driver.find_element_by_id("a-autoid-0-announce")
        country_dropdown.click()
        time.sleep(1)

        c_element = self.driver.find_element_by_id("icp-selected-country_{0!s}".format(index))
        c_element.location_once_scrolled_into_view
        time.sleep(1)

        self.driver.execute_script("arguments[0].click()", c_element)
        time.sleep(1)

        base_logger.info("{0!s} should now be chosen - Scrolling to top of page".format(country))
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

        return

    def newTab(self, cleanup=False):
        """
        :param:cleanup (Optional) : Bool stating whether or not to run metrics
        :return:country_change : Bool representing success or failure of finding requested country in available list
        """
        perf = p()
        country_change = False

        current_page = self.driver.current_window_handle
        current_title = self.driver.title

        base_logger.info("Current page title is: {0!s}".format(current_title))

        base_logger.info("Clicking enter to change countries now.. Expect a new tab to open up...")
        
        c_submit = self.driver.find_element_by_id("a-autoid-2-announce")
        time.sleep(1)

        if not cleanup:
            metrics = perf.calcStatsLAS(self.driver)

        self.driver.execute_script("arguments[0].click()", c_submit)
        time.sleep(2)

        children = self.driver.window_handles

        base_logger.info("Child handles are: {0!s}".format(children))

        for child in children:
            if child != current_page:
                base_logger.info("Switching focus to new tab now...")
                self.driver.switch_to.window(child)
                new_title = self.driver.title.encode('ascii', 'ignore')
                base_logger.info("New title is: {0!s}".format(new_title))

        if new_title != current_title:
            base_logger.info("Changed to a new country successfully")
            country_change = True

        if cleanup:
            return country_change, None
        else:
            return country_change, metrics

    def countryCleanup(self):
        """
        :param:
        :return:country_cleanup : Bool representing success or failure of reverting to current country
        """
        country_cleanup = False
        
        self.setFocus()
        c_page = self.findCountry()
        if c_page:
            found, index = self.selectIndex(country=self.current_country)
            if found:
                self.chooseCountry(index, country=self.current_country)
                c_change, metrics = self.newTab(cleanup=True)
                if c_change:
                    country_cleanup = True
                    base_logger.info("Country has been reverted to {0!s}".format(self.current_country))

        return country_cleanup








            


        
