from simple_setup import *
from simple_setup import simpleSetup as s
from load_and_search import loadAndSearch as las
from perf_analysis import perfAnalysis as p
from sign_in import signIn as si
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import logging
import datetime
import time

class addToCart(simpleSetup):
    def __init__(self):
        super(addToCart, self).__init__()

    def readCart(self, driver):
        """
        :param:driver : web driver instance
        :return:
        """
        base_logger.info("Reading config file for 'Add To Cart' tests now...")
        self.driver = driver
        
        l = las()
        cart_config = l.readConfig()

        self.atc_search_link = cart_config['SignIn']['load_link']
        self.atc_link_assert = cart_config['Search']['link_assert'].encode('ascii', 'ignore')
        self.atc_search_item = cart_config['Cart']['search_item'].encode('ascii', 'ignore')
        self.atc_search_dept = cart_config['Cart']['search_dept'].encode('ascii', 'ignore')
        self.atc_lookup_1 = cart_config['Cart']['item_lookup_1'].encode('ascii', 'ignore')
        self.atc_lookup_2 = cart_config['Cart']['item_lookup_2'].encode('ascii', 'ignore')
        self.atc_lookup_3 = cart_config['Cart']['item_lookup_3'].encode('ascii', 'ignore')
        self.atc_oq = cart_config['Cart']['order_quantity'].encode('ascii', 'ignore')
        self.atc_coupon = cart_config['Cart']['coupon_clip'].encode('ascii', 'ignore')

        return

    def checkHomePage(self):
        """
        :param:
        :return:home_page: Bool representing success or failure of launching right home page
        """
        home_page = False

        if self.atc_link_assert in self.driver.title and "Sign-In" not in self.driver.title:
            base_logger.info("On the right landing page. Moving onto 'Add to Cart' tests now...")
            home_page = True
        else:
            base_logger.error("Not on right landing page for 'Add to Cart' tests. Re-running 'Sign-In' now...")
            self.driver.get(self.atc_search_link)
            time.sleep(2)
            
            sg_in = si()
            
            sg_in.readSignIn(self.driver)
            sg_in.logInPage()
            sg_in.logIn(rerun=True)
            login = sg_in.verifySignIn()
            
            if login:
                home_page = True
        
        return home_page

    def navToDropdown(self, browser):
        """
        :param:
        :return:dd_success: Bool representing success or failure of choosing required department
        """
        base_logger.info("Starting Automated Item Search")
        
        dd_success = False

        if browser == "Firefox" or browser == "firefox" or browser == "ff" or browser == "Safari":
            dd_ff_success = self.navtoDropdownFF(browser)
            return dd_ff_success
        else:
            options_dict = {}
            try:
                base_logger.info("Locating dropdown for Amazon's shopping departments...")
                selections = Select(self.driver.find_element_by_id('searchDropdownBox'))
                for option in selections.options:
                    options_dict[option.get_attribute('value')] = option.text 
                if self.atc_search_dept in options_dict.values():
                    base_logger.info("Found the {0!s} department in dropdown - proceeding to choose it...".format(self.atc_search_dept))
                    
                    dropdown = self.driver.find_element_by_id('nav-search-dropdown-card').click()
                    time.sleep(3)
                        
                    selections.select_by_visible_text(self.atc_search_dept)
                    time.sleep(3)
                    
                    final_selection = (selections.first_selected_option).text
                    
                    if final_selection == self.atc_search_dept:
                        base_logger.info("Right department has been chosen on webpage. Moving onto search...")
                        dd_success = True
            
            except Exception as e:
                base_logger.error("Failed to choose department due to : {0!s}".format(e))
        
        return dd_success

    def navtoDropdownFF(self, browser):
        """
        :param:
        :return:dd_ff_success: Bool representing success or failure of choosing right department on Firefox
        """
        dd_ff_success = False
        base_logger.info("Selecting department {0!s} on {1!s} now...".format(self.atc_search_dept, browser))
        
        try:
            search_box = self.driver.find_element_by_id('twotabsearchtextbox')
            time.sleep(4)
            search_box.send_keys(self.atc_search_dept)
            time.sleep(4)

            submit_button = self.driver.find_element_by_id('nav-search-submit-text')
            time.sleep(4)
            submit_button.click()
            time.sleep(4)

            base_logger.info("Finding & clicking on {0!s} in the side bar".format(self.atc_search_dept))
            sidebar = self.driver.find_element_by_xpath("//span[text()='{0!s}']".format(self.atc_search_dept))
            time.sleep(4)
            sidebar.click()
            time.sleep(2)
            
            base_logger.info("Clearing search box for future entries now...")
            search_box_again = self.driver.find_element_by_id('twotabsearchtextbox')
            time.sleep(3)
            search_box_again.click()
            time.sleep(3)
            search_box_again.clear()
            time.sleep(3)

        except Exception as e:
            base_logger.error("Failed to find department on {0!s} due to : {1!s}".format(browser, e))

        selections = Select(self.driver.find_element_by_id('searchDropdownBox'))
        selected_dept = selections.first_selected_option.text
        
        if self.atc_search_dept == selected_dept:
            base_logger.info("Right department has been chosen on {0!s} webpage. Moving onto search...".format(browser))
            dd_ff_success = True

        return dd_ff_success

    def navToSearch(self, browser):
        """
        :param:
        :return:search_success: Bool representing success or failure of running required search
        """
        search_success = False
        perf = p()
        base_logger.info("Locating search box now...")
        
        try:
            search_element = self.driver.find_element_by_id("twotabsearchtextbox")
            time.sleep(2)
            search_element.click()
            time.sleep(2)
            search_element.send_keys(self.atc_search_item)
            time.sleep(4)
            
            metrics = perf.calcStatsLAS(self.driver)

            self.driver.find_element_by_id("nav-search-submit-text").click()
            time.sleep(5)

            res_element_found = self.driver.find_element_by_xpath('//*[@id="search"]/span/div/span')
            time.sleep(3)
            
            res_element = res_element_found.text.encode('ascii', 'ignore')

            if browser == "Safari":
                res_element = res_element.replace("\n","")
                res_element = res_element.split('Sort')[0].strip()
            else:
                res_element = res_element.split('\n')[0].strip()

            if self.atc_search_item and "results" in res_element:
                num_of_res = int(res_element.split(" ")[2].strip())
                
                if num_of_res > 0:
                    base_logger.info("Successfully obtained {0!s} search results for {1!s}".format(num_of_res, self.atc_search_item))
                    search_success = True

        except Exception as e:
            base_logger.error("Failed to find search results due to : {0!s}".format(e))

        return search_success, metrics

    def locateItem(self, browser):
        """
        :param:
        :return:locate_success: Bool representing success or failure of finding matching search item
        :return:clicked_item: Text of item chosen to be added to cart
        """
        found_elements = []
        locate_success = False
        base_logger.info("Locating matching item now...")

        self.browser = browser

        try:
            all_a_elems = self.driver.find_elements_by_xpath('//a[@href]')
    
            for element in all_a_elems:
                one_href = element.get_attribute("href")
                if self.atc_search_item in one_href:
                    if self.atc_lookup_1 and self.atc_lookup_2 and self.atc_lookup_3 in one_href:
                        found_elements.append(element)

            base_logger.info("Clicking on last item in search list now...")
            
            item_interest = found_elements[len(found_elements)-3]
            item_text = str(item_interest.text).strip()
            base_logger.info("Item being picked - {0!s}".format(item_text))
            
            if self.browser=="Firefox" or self.browser=="firefox" or self.browser=="ff":
                self.scrollForFF(item_interest)
                time.sleep(5)
                if item_interest.is_displayed():
                    base_logger.info("{0!s} has displayed item on viewport".format(self.browser))
                    ff_elem = ActionChains(self.driver).move_to_element(item_interest)
                    time.sleep(3)
                    ff_elem.click().perform()
                    time.sleep(4)
            elif self.browser == "Safari":
                link = item_interest.get_attribute("href")
                self.driver.get(link)
                time.sleep(4)
            else:
                item_interest.click()
                time.sleep(4)

            clicked_item = str(self.driver.find_element_by_id("productTitle").text).strip()
            time.sleep(2)

            base_logger.info("Following product has been loaded - {0!s}".format(clicked_item))

            if clicked_item == item_text:
                base_logger.info("Clicked on an matching search item. Proceeding to clip coupon/add to cart...")
                
                if self.atc_coupon == "True":
                    self.clipCoupon(clicked_item)
                
                locate_success = True
        
        except Exception as e:
            base_logger.error("Failed to choose department due to : {0!s}".format(e))

        return locate_success, clicked_item

    def scrollForFF(self, element):
        """
        :param:element: object to be scrolled to
        :return:
        """
        self.driver.execute_script('arguments[0].scrollIntoView(true);', element)
        time.sleep(2)

        return

    def chooseQuantity(self, browser):
        """
        :param:
        :return:choose_success: Bool representing success or failure of adding requested quantity of item
        """
        choose_success = False

        if browser == "Firefox" or browser == "firefox" or browser == "ff" or browser=="Safari":
            choose_ff_success = self.chooseQuantityFF(browser)
            
            return choose_ff_success
        else:
            options_dict = {}
            base_logger.info("Choosing right quantity  - {0!s} - for item now...".format(self.atc_oq))

            try:
                selections = Select(self.driver.find_element_by_id("quantity"))
                
                for options in selections.options:
                    options_dict[options.get_attribute('value')] = options.text.encode('ascii', 'ignore')
                            
                if self.atc_oq in options_dict.values():
                    dropdown = self.driver.find_element_by_class_name("a-dropdown-container").click()
                    time.sleep(2)

                    selections.select_by_visible_text(self.atc_oq)
                    time.sleep(2)

                    if self.browser=="Firefox" or self.browser=="firefox" or self.browser=="ff":
                        dropdown.click()
                        time.sleep(2)

                    final_selection = (selections.first_selected_option).text

                    if final_selection in self.atc_oq:
                        base_logger.info("Right quantity has been chosen on webpage. Moving onto adding to cart...")
                        choose_success = True
            
            except Exception as e:
                base_logger.error("Failed to choose quantity due to : {0!s}".format(e))

        return choose_success

    def chooseQuantityFF(self, browser):
        """
        :param:
        :return:choose_ff_success: Bool representing success or failure of adding requested quantity of item on FF
        """
        choose_ff_success = False
        options_list = []

        base_logger.info("Choosing right quantity  - {0!s} - for item now on {1!s}...".format(self.atc_oq, browser))
        
        try:
            quantity_dropbox = self.driver.find_element_by_id('a-autoid-0')
            time.sleep(2)
            selection_list = self.driver.find_element_by_id('quantity')
            time.sleep(2)
            product_title = self.driver.find_element_by_id('productTitle')
            time.sleep(2)

            selections = Select(selection_list)
            options = selections.options

            [options_list.append(str(x.text.encode('ascii', 'ignore')).strip()) for x in options]

            if self.atc_oq in options_list:
                base_logger.info("Requested quantity of {0!s} is available for selection".format(self.atc_oq))
                
                if self.browser == "Firefox" or self.browser == "firefox" or self.browser == "ff":
                    quantity_dropbox.click()
                    selection_list.send_keys(self.atc_oq)
                    product_title.click()

                else:
                    for iteration in range(1, int(self.atc_oq)+1):
                        base_logger.info("Adding item via 'Add to Cart' action on Safari browser")
                        
                        self.driver.find_element_by_id("add-to-cart-button").click()
                        time.sleep(3)
                        
                        if iteration != int(self.atc_oq):
                            self.driver.back()
                            time.sleep(2)
                        
                        base_logger.info("Added item {0!s} time".format(iteration))
                        
                    choose_ff_success = True

                    return choose_ff_success

        except Exception as e:
            base_logger.error("Failed to choose quantity on Firefox due to : {0!s}".format(e))

        if selections.first_selected_option.text == self.atc_oq:
            base_logger.info("Successfully updated product quantity to {0!s}".format(self.atc_oq))
            choose_ff_success = True

        return choose_ff_success

    def addItemToCart(self, clicked_item):
        """
        :param:clicked_item: Text of item chosen to be added to cart
        :return:add_success: Bool representing success or failure of adding item to cart
        """
        add_success = False
        
        try:
            if self.browser != "Safari":
                base_logger.info("Adding item(s) to cart now...")
                cart_element = self.driver.find_element_by_id("add-to-cart-button").click()
                time.sleep(2)

            if "Added to Cart" in self.driver.page_source:
                base_logger.info("Cart has been successfully populated with {0!s} quantity of {1!s}...".format(self.atc_oq, clicked_item))
                add_success = True
        
        except Exception as e:
            base_logger.error("Failed to add item(s) to cart due to : {0!s}".format(e))

        return add_success

    def clipCoupon(self, clicked_item):
        """
        :param:clicked_item: Text of item chosen to be added to cart
        :return:
        """
        base_logger.info("Checking for coupons to clip...")

        try:
            coupon = self.driver.find_element_by_xpath("//*[@id='vpcButton']/div/label/i")
            
            if coupon:
                base_logger.info("Found & clipped a coupon!")
                coupon.click()
                time.sleep(1)
                
                c_coupon = self.driver.find_element_by_xpath("//*[@id='vpcButton']/div/label/i")
                
                if c_coupon.is_selected():
                    base_logger.info("Coupon clip went through successfully")
                else:
                    base_logger.error("Coupon clip seems to have failed")
            
            else:
                base_logger.error("No coupon has been found for {0!s}".format(clicked_item))
        
        except Exception as e:
            base_logger.error("Failed to clip coupon due to : {0!s}".format(e))
        
        return

    def cartCleanup(self, browser, preflight=False):
        """
        :param:
        :return:cart_cleanup: Bool representing success or failure of cart cleanup operation
        """
        cart_cleanup = False

        base_logger.info("Cleaning up cart to reset to zero items...")

        if preflight:
            self.driver.find_element_by_id("nav-cart").click()
            time.sleep(1)
        else:
            self.driver.find_element_by_id("hlb-view-cart").click()
            time.sleep(1)

        tmp_list = []
        items_to_delete = []
        
        tmp_list = self.driver.find_elements_by_tag_name("input")
        
        for tmp_item in tmp_list:
            if tmp_item.get_attribute('value') == "Delete":
                items_to_delete.append(tmp_item)

        if items_to_delete:

            if browser == "Safari":
                count = 0
                for iteration in range(len(items_to_delete)):
                    tmp_s_list = []
                    safari_list = []
                    tmp_s_list = self.driver.find_elements_by_tag_name("input")
                    for item in tmp_s_list:
                        count+=1
                        if item.get_attribute('value') == "Delete":
                            base_logger.info("Using Safari browser - deleting item {0!s} during iteration {1!s}".format(item.text, count))
                            time.sleep(2)
                            self.driver.execute_script('arguments[0].click()',item)
                            time.sleep(3)
                            break
                        else:
                            pass
            else:
                for item in items_to_delete:
                    if browser != "Firefox":
                        item.location_once_scrolled_into_view
                    item.click()
                    time.sleep(1)
                if browser != "Firefox":
                    self.driver.execute_script("window.scrollTo(0, 0);")

        else:
            base_logger.info("Cart already appears to be empty...")

        if "Your Amazon Cart is empty." in self.driver.page_source:
            cart_cleanup = True
            base_logger.info("Cart Cleanup completed successfully")
            time.sleep(2)

        return cart_cleanup

        



        
            
