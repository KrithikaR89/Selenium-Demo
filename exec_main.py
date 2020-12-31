from simple_setup import *
from simple_setup import simpleSetup
from load_and_search import loadAndSearch
from perf_analysis import perfAnalysis
from sign_in import signIn
from add_to_cart import addToCart
from country import country 
import logging
import json
import shutil

def setupTools():
    """
    :param: 
    return:driver_load : Bool representing success of driver initializatio
    :return:driver : webdriver instance
    """
    config = st._readConfig()
    browser, headless, page = st.initConfig(config)
    driver_load, driver = st.initDriver()

    return browser, headless, page, driver_load, driver

def readSetupConfig():
    """
    :param:
    :return: test_cycles for testing iterations
    :return: search_flag for load & search testing enablement
    :return: user_flag for user flow testing enablement
    """
    with open("setup.json", 'r') as f:
        setup = json.load(f)
    test_cycles = int(setup['iterations'])
    pflight = str(setup['preflight'])
    search_flag = str(setup['search_tests'])
    user_flag = str(setup['user_flow_tests'])
    cart_flag = str(setup['user_flow_add_to_cart'])
    country_flag = str(setup['user_flow_country'])

    base_logger.info("----------TEST SETUP DETAILS----------")
    base_logger.info("Requested Testing iterations : {0!s}".format(test_cycles))
    base_logger.info("Requested Pre-flight : {0!s}".format(pflight))
    base_logger.info("Requested Test Scenario - Load & Search: {0!s}".format(search_flag))
    base_logger.info("Requested Test Scenario - User Flow : {0!s}".format(user_flag))
    base_logger.info("Requested Test Scenario - User Flow - Add to Cart: {0!s}".format(cart_flag))
    base_logger.info("Requested Test Scenario - User Flow - Country Change: {0!s}".format(country_flag))

    return test_cycles, pflight, search_flag, user_flag, cart_flag, country_flag

def documentPreflight():
    """
    :param:
    :return:
    """
    base_logger.info("Cleaning up working directory...")
    
    res_file_list = ['web_', 'las_', 'uf_', 'cc_']
    
    all_files = os.listdir(os.getcwd())

    for res in res_file_list:
        for dir_file in all_files:
            if res in dir_file:
                if time_stamp not in dir_file:
                    base_logger.info("Removing file {0!s} from CWD".format(dir_file))
                    if os.path.exists(dir_file):
                        os.remove(dir_file)

    return

def preflight(driver, browser):
    """
    :param: driver : webdriver instance
    :return: preflight_status : Bool representing success of preflight cleanup
    """
    base_logger.info("Initiating Pre-Flight")
    
    ac.readCart(driver)
    hp_success = ac.checkHomePage()
    if hp_success:
        base_logger.info("Initial log-in successful - Checking cart to remove stray items...")
        cp_success = ac.cartCleanup(browser, preflight=True)
        
        if cp_success:
            base_logger.info("Cart cleanup successful - Signing out of profile now...")
            signout_success = si.signOut(browser,driver)
            
    return signout_success

def runLAS(driver_load, driver):
    """
    :param: driver_load : Bool representing success of driver initialization
    :param: driver : webdriver instance
    :return: lnk_status : Bool representing success of web page search & load
    :return: metrics : Metrics collected as part of perf analysis
    """
    base_logger.info("Result for driver load is: {0!s}. Moving onto Webpage load/Search tests".format(driver_load))
    
    las_config = las.readConfig()
    las.initLoad(las_config)
    load_success = las.loadPage(driver)
    
    if load_success:
        s_status = las.searchPage()
        if s_status:
            lnk_status, metrics = las.redirLink()
    
    return lnk_status, metrics

def runSI(driver):
    """
    param:
    return: si_success : Bool representing success of signin process
    """
    si.readSignIn(driver)
    si.logInPage()
    si_metrics = si.logIn()
    si_success = si.verifySignIn()

    return si_success, si_metrics

def runATC(driver, browser):
    """
    param:
    return: cleanup_success : Bool representing success of Add to Cart process
    """
    ac.readCart(driver)
    home_page_success = ac.checkHomePage()
    if home_page_success:
        dropdown_success = ac.navToDropdown(browser)
        search_success, atc_metrics = ac.navToSearch(browser)
        if search_success:
            locate_success, clicked_item = ac.locateItem(browser)
            if locate_success:
                choose_success = ac.chooseQuantity(browser)
                if choose_success:
                    add_success = ac.addItemToCart(clicked_item)
                    if add_success:
                        cleanup_success = ac.cartCleanup(browser)
                        if not cleanup_success:
                            base_logger.error("ATC - Error with post testing cart cleanup")
                    else:
                        base_logger.error("ATC - Error with adding items to cart")
                else:
                    base_logger.error("ATC - Error with choosing right quantity")
            else:
                base_logger.error("ATC - Error with locating matching item")
        else:
            base_logger.error("ATC - Error with obtaining search results")
    else:
        base_logger.error("ATC - Error with not being on right home page")

    return cleanup_success, atc_metrics

def runCC(driver):
    """
    param:
    return: cleanup : Bool representing success of signin process
    """
    cc_success = False

    c.readCountry(driver)
    c.setFocus()
    page = c.findCountry()
    if page:
        found, index = c.selectIndex()
        if found:
            c.chooseCountry(index)
            change, c_metrics = c.newTab()
            if change:
                cleanup = c.countryCleanup()
            else:
                base_logger.error("CC - Error with not being able to execute country switch")
        else:
            base_logger.error("CC - Error with not being able to find position of requested country on list")
    else:
        base_logger.error("CC - Error with not being able to land on country selection page")

    return cleanup, c_metrics

def writeData(count, metrics, test_type="las"):
    """
    :param:count : Iteration currently being executed
    :param:metrics: Stats generated for specific iteration
    return:
    """
    metrics.insert(0,'Iteration'+' '+str(count))
    base_logger.info("List to be written to csv is {0!s}".format(metrics))
    
    if count==1:
        if test_type == "las":
            csv_name = 'las_web_metrics_{0!s}.csv'.format(time_stamp)
        elif test_type == "uf":
            csv_name = 'uf_web_metrics_{0!s}.csv'.format(time_stamp)
        elif test_type == "atc":
            csv_name = 'atc_web_metrics_{0!s}.csv'.format(time_stamp)
        else:
            csv_name = 'cc_web_metrics_{0!s}.csv'.format(time_stamp)
    else:
        csv_files = os.listdir(os.getcwd())
        for new_file in csv_files:
            if new_file.endswith('.csv') and test_type in new_file:
                csv_name = new_file
    
    pa.writeStats(metrics, csv_name, count)
    
    return

def logCollection():
    """
    param:
    return:res_folder : Directory holding all final results
    return:csv_name : List of csv result files
    """
    res_folder, csv_name = st.logpull()
    
    pa.plotGraph(res_folder, csv_name)
    
    return res_folder, csv_name

def clumpLogs(res_folder, csv_name):
    """
    param:res_folder : Directory holding all final results
    param:csv_name : List of csv result files
    return:
    """
    base_logger.info("CWD is : {0!s}".format(os.getcwd()))
    
    os.mkdir("Graphs")
    
    for csv in csv_name:
        csv_type = csv.split("_")[0].strip().upper()+' '+'graphs'
        full_path = os.getcwd()+'/'+'Graphs'+'/'+csv_type
        os.chdir("Graphs")
        os.mkdir("{0!s}".format(csv_type))
        os.chdir("..")
        
        for r_file in os.listdir(os.getcwd()):
            if "png" in r_file and "Iteration" in r_file and csv.split("_")[0].strip() in r_file:
                shutil.move(r_file, full_path)
                tmp_res_path = full_path+'/'+r_file
                
                if os.path.exists(tmp_res_path):
                    base_logger.info("Moved {0!s} successfully to folder {1!s}".format(r_file, csv_type))

    base_logger.info("Logs should now be grouped")

    return

if __name__ == '__main__':
    start_time = datetime.datetime.now()

    base_logger.info("Starting Browser Automation tests at {0!s}"
        .format(start_time.strftime("%D %I:%M:%S %p")))
    
    base_logger.info("*********************************************************")
    
    test_cycles, pflight, search_flag, user_flag, cart_flag, country_flag = readSetupConfig()
    
    st = simpleSetup()
    las = loadAndSearch()
    pa = perfAnalysis()
    si = signIn()
    ac = addToCart()
    c = country()
    documentPreflight()
    
    preflight_check = False
    results_dict = {}

    if search_flag == "True" or user_flag == "True" or cart_flag == "True" or country_flag == "True":
        for count in range(1, test_cycles+1):
            base_logger.info("Running Web Test iteration {0!s} as {1!s}".format(count, datetime.datetime.now().strftime('%D, %I:%M:%S %p')))
            
            if search_flag == "True":
                base_logger.info("~~~ Initializing driver for LAS iteration {0!s} ~~~".format(count))
                browser, headless, page, driver_load, driver = setupTools()

                if driver_load:

                    if pflight == "True" and not preflight_check:
                        preflight_status = preflight(driver, browser)
                        if preflight_status:
                            base_logger.info("Pre-flight setup was successful")
                            preflight_check = True
                        else:
                            base_logger.error("Pre-flight setup has failed - could cause issues during testing")

                    lnk_status, metrics = runLAS(driver_load, driver)
                    if metrics:
                        writeData(count, metrics, test_type="las")
                    
                    results_dict["Load & Search"] = lnk_status
                    
                    st.teardown()
                
                else:
                    base_logger.error("Cannot run any testing on iteration {0!s} as driver did not load".format(count))
            
            if user_flag == "True" or cart_flag == "True" or country_flag == "True":
                browser, headless, page, driver_load, driver = setupTools()

                if driver_load:

                    if pflight == "True" and not preflight_check:
                        preflight_status = preflight(driver, browser)
                        if preflight_status:
                            base_logger.info("Pre-flight setup was successful")
                            preflight_check = True
                        else:
                            base_logger.error("Pre-flight setup has failed - could cause issues during testing")
                    
                    if user_flag == "True":
                        base_logger.info("~~~ Initializing driver for UF iteration {0!s} ~~~".format(count))
                        si_status, si_metrics = runSI(driver)
                        if si_status and si_metrics:
                            writeData(count, si_metrics, test_type="uf")
                        
                        results_dict["User Flow"] = si_status
                    
                    if cart_flag == "True":
                        base_logger.info("~~~ Initializing driver for ATC iteration {0!s} ~~~".format(count))
                        cart_status, atc_metrics = runATC(driver, browser)
                        so_success = si.signOut(browser, driver)
                        if atc_metrics:
                            writeData(count, atc_metrics, test_type="atc")
                        
                        results_dict["User Flow - Add to Cart"] = cart_status

                    if country_flag == "True":
                        base_logger.info("~~~ Initializing driver for CC iteration {0!s} ~~~".format(count))
                        cleanup, c_metrics = runCC(driver)
                        c_so_success = si.signOut(browser, driver)
                        if c_metrics:
                            writeData(count, c_metrics, test_type="cc")
                        
                        results_dict["User Flow - Country Change"] = cleanup

                    st.teardown(special=True)
                
                else:
                    base_logger.error("Cannot run any testing on iteration {0!s} as driver did not load".format(count))
            
            preflight_check = False
        
        res_folder, csv_name = logCollection()

        clumpLogs(res_folder, csv_name)
    else:
        base_logger.error("No test scenarios have been selected for run. Tearing down.")
    
    end_time = datetime.datetime.now()
    
    test_duration = str(end_time - start_time).split(".")[0]

    test_duration = test_duration.split(":")

    test_hours = str(test_duration[0])
    test_minutes = str(test_duration[1])
    test_seconds = str(test_duration[2])

    base_logger.info("----------------------------------------------------------")
    
    base_logger.info("                  FINAL TEST RESULTS                      ")

    base_logger.info("----------------------------------------------------------")

    base_logger.info("Number of Test Iterations Requested - {0!s}".format(test_cycles))

    base_logger.info("Total Test Time Elapsed  - {0!s} hours, {1!s} minutes, {2!s} seconds".format(test_hours, test_minutes, test_seconds))

    for key, value in results_dict.items():
        if value == True:
            result_str = "TEST PASSED"
        else:
            result_str = "TEST FAILED"
        
        base_logger.info("Test Scenario {0!s} has been completed - {1!s}".format(key, result_str))

    base_logger.info("Ending Browser Automation tests at {0!s}"
        .format(end_time.strftime("%D %I:%M:%S %p")))
    
    base_logger.info("*********************************************************")