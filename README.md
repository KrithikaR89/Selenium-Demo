Selenium Hobby Project scripted with Python, working with chromedriver, geckodriver, & safaridriver
This code runs through 4 different tests cases, for as many iterations as configured by the user:
1. Basic Search : Load www.google.com, enter a string to search, wait for search results, click on link matching search string, load resulting webpage
2. User Flow - Account Sign in : Load www.amazon.com, Sign-in to account, verify sign in success
3. User Flow - Add item to cart : Load www.amazon.com, Sign-in to account, switch to a requested shopping department, key in an item to search, find an item that meets all expected search criteria, click on item's link, & add requested quantity of item into cart. Once the item's addition has been confirmed, delete all itms in cart & sign out of account
4. User Flow - Change country : Load www.amazon.com, Sign-into account, head to country/region settings, change to requested country, verify change, switch back to original country, sign out
During all these 4 tests cases, the code will also capture these performance metrics for specific webpage load activities:
1. Frontend load time
2. Backend time
3. Network Traversal time
4. User percieved load time
Using these metrics, the automation will calculate 95th percentile, 90th percentile, 50th percentile, & Standard Deviation for these numbers across iterations, graph the respective metrics & post the calculated stats on the graphs.
Finally, the code will also run cleanup/housekeeping making sure the account settings are reset (cart is back to zero items, country is back to current country). All Logs (including the geckodriver.log for Firefox) will be grouped together conveniently under CWD/Logs/<Browser_name>Logs directory. Graphs are further grouped based on the scenario (Search/Userflow etc) during which they were captured.
Users are able to configure every aspect of test run including which test cases to run, which browser to run against, iterations to run, website to launch, country to be selected etc. The file config.json controls the minutia of each test case whereas the setup.json file controls the overall test run itself.
