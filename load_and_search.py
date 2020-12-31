from simple_setup import *
from simple_setup import simpleSetup as s
from perf_analysis import perfAnalysis as p
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import logging

class loadAndSearch(simpleSetup):
    def __init__(self):
        super(loadAndSearch, self).__init__()

    def readConfig(self):
        """
        param:
        return:config: Dict containing relevant config values
        """
        
        config = s._readConfig(self)

        return config

    def initLoad(self,config):
        """
        param: Dict containing relevant config values
        return:
        """
        base_logger.info("Here are the page load items...")
        
        self.webpage = config['Load']['page']
        base_logger.info("Requested website is: {0!s}".format(self.webpage))
        
        self.l_assert = str(config['Load']['page_assert'].encode('ascii', 'ignore'))
        base_logger.info("Requested page assert is: {0!s}".format(self.l_assert))
        
        self.s_string = str(config['Search']['search_string'].encode('ascii', 'ignore'))
        base_logger.info("Requested search string is: {0!s}".format(self.s_string))

        self.s_link = str(config['Search']['search_link'].encode('ascii', 'ignore'))
        base_logger.info("Requested search link is: {0!s}".format(self.s_link))

        self.lnk_assert = str(config['Search']['link_assert'].encode('ascii', 'ignore'))
        base_logger.info("Requested link assert is: {0!s}".format(self.lnk_assert))

        return
        
    def loadPage(self, driver):
        """
        param:
        return:load_success : Bool value representing outcome of page load action
        """

        self.driver = driver
        load_success = False
        
        if self.webpage and self.l_assert:
            
            base_logger.info("Launching website {0!s} now...".format(self.webpage))
            self.driver.maximize_window()
            self.driver.get(self.webpage)
            base_logger.info("Recording performance stats now...")
            
            try:
                if self.l_assert in self.driver.title:
                    base_logger.info("{0!s} has loaded successfully!".format(self.webpage))
                    load_success = True
            except Exception as e:
                base_logger.error("Tearing down. Failed to load webpage due to {0!s}".format(e))

        return load_success

    def searchPage(self):
        """
        param:
        return:search_status: Bool value representing outcome of page search action
        """
        search_status = False
            
        base_logger.info("Finding search bar on webpage...")

        elem=self.driver.find_element_by_name("q")
        
        if elem:
            base_logger.info("Found search field! Clearing it now...")
            elem.clear()
            
            base_logger.info("Entering search criteria...")
            elem.send_keys(self.s_string)
            elem.send_keys(Keys.RETURN)
            
            time.sleep(10)
            
            search_status = True
        else:
            base_logger.error("Tearing down.Could not locate a search bar on page")
        
        return search_status

    def redirLink(self):
        """
        param:
        return:redir_status: Bool value representing outcome of link click action
        """
        perf = p()
        link_status = False

        base_logger.info("Going to click on redirect link now...")

        wait = WebDriverWait(self.driver, 10)
        link = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT,self.s_link)))
        
        if link:
            base_logger.info("Found the right redirect link... Clicking now...")
            self.driver.execute_script('arguments[0].click()', link)
            # link_click = ActionChains(self.driver).move_to_element(link)
            # time.sleep(5)
            # link_click.click().perform()
            metrics = perf.calcStatsLAS(self.driver)
            time.sleep(20)
            try:
                if self.lnk_assert in self.driver.title:
                    link_status = True
            except Exception as e:
                base_logger.error("Tearing down. Failed to load webpage due to {0!s}".format(e))

        return link_status, metrics



