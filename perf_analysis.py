from __future__ import division
from simple_setup import *
from simple_setup import simpleSetup as s
import logging
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class perfAnalysis(simpleSetup):
    def __init__(self):
        super(perfAnalysis, self).__init__()

    def calcStatsLAS(self, driver):
        """
        :param:data : perf data list from window.performance measurement during page load
        :return: list of calculated data to be written to a spreadsheet
        """
        nav_start = driver.execute_script('return window.performance.timing.navigationStart;')
        nav_start = round((nav_start/1000), 3)
        base_logger.info("Navigation Start has been calculated as - {0!s}".format(nav_start))
        
        dom_evt_end = driver.execute_script('return window.performance.timing.domContentLoadedEventEnd;')
        dom_evt_end = round((dom_evt_end/1000), 3)
        base_logger.info("DOM Content Loaded has been calculated as - {0!s}".format(dom_evt_end))

        full_load = driver.execute_script('return window.performance.timing.loadEventEnd;')
        full_load = round((full_load/1000), 3)
        base_logger.info("Full Load has been calculated as - {0!s}".format(full_load))

        net_start = driver.execute_script('return window.performance.timing.domainLookupStart;')
        net_start = round((net_start/1000), 3)
        base_logger.info("Network Start has been calculated as - {0!s}".format(net_start))

        net_end = driver.execute_script('return window.performance.timing.responseEnd;')
        net_end = round((net_end/1000), 3)
        base_logger.info("Network End has been calculated as - {0!s}".format(net_end))

        base_logger.info("Calculating Stats now...")
        frontend_load = round((dom_evt_end - nav_start), 3)
        backend_load = round((dom_evt_end - net_end), 3)
        network_timing = round((net_end - net_start), 3)
        user_percieved_timing = round((full_load - nav_start), 3)
        
        base_logger.info("Webpage Performance Stats : ")
        base_logger.info("Time taken to load only FrontEnd : {0!s}s".format(frontend_load))
        base_logger.info("Time taken to load only Backend : {0!s}s".format(backend_load))
        base_logger.info("Time taken to traverse network : {0!s}s".format(network_timing))
        base_logger.info("Time taken for full user-perceived load : {0!s}s".format(user_percieved_timing))

        return [frontend_load, backend_load, network_timing, user_percieved_timing]

    def writeStats(self, metrics, csv_name, count):
        """
        :param: list of calculated data to be written to a spreadsheet
        :return: 
        """
        base_logger.info("Creating/Updating CSV file with web metrics")

        if count==1:
            df = pd.DataFrame(data=[metrics], columns=['Iteration','Frontend Load Time (secs)', 'Backend Load Time (secs)', 
            'Network Transfer Time (secs)', 'User Percieved Load Time (secs)'])
            df = df[(df > 0).all(1)] #Removing negative numbers from dataframe due to 0.0 timings
            if not df.empty:
                df.to_csv(csv_name)
            else:
                base_logger.info("Did not write data into CSV during iteration {0!s} - Negative data set present".format(count))
                df = pd.DataFrame(columns=['Iteration','Frontend Load Time (secs)', 'Backend Load Time (secs)', 
                'Network Transfer Time (secs)', 'User Percieved Load Time (secs)'])
                df.to_csv(csv_name)
        else:
            df = pd.DataFrame(data=[metrics])
            df = df[(df > 0).all(1)]
            if not df.empty:
                df.to_csv(csv_name, mode='a', header=False)
            else:
                base_logger.info("Did not write data into CSV during iteration {0!s} - Negative data set present".format(count))
        
        return

    def plotGraph(self, res_folder, csv_name):
        """
        :param: Completed spreadsheet to be plotted
        :return: 
        """
        axis_list = []

        full_path = os.getcwd()+'/'+'Logs'+'/'+res_folder
        os.chdir(full_path)
        
        for csv in csv_name:
            test_type = csv.split("_")[0].strip()

            self.df = pd.read_csv(csv)

            if not self.df.empty:
                xaxis = "Iteration"

                for i in self.df.columns:
                    if "secs" in i:
                        axis_list.append(i)
                try:
                    for item in axis_list:
                        
                        stats = self.calcPerc(item)
                        
                        text_str_95 = "P(95) is: {0!s}".format(stats['95'])
                        text_str_90 = "P(90) is: {0!s}".format(stats['90'])
                        text_str_50 = "P(50) is: {0!s}".format(stats['50'])
                        text_str_sd = "SD is: {0!s}".format(stats['Std Dev'])
                        text_str = 'Stats are: ' +'\n' + text_str_95 + '\n' + text_str_90 + '\n' + text_str_50 + '\n' + text_str_sd

                        base_logger.info("Generating plot for {0!s} vs {1!s} - ({2!s}) now...".format(xaxis,item, test_type))

                        fig, ax = plt.subplots()
                        
                        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
                        
                        if len(self.df)==1:
                            self.df.plot(x=xaxis, y=item, label=item, ylim=(0,3.5), marker='o')
                        else:
                            self.df.plot(x=xaxis, y=item, label=item)
                        
                        y_label = item.split("(")[0].strip()
                        
                        plt.title('{0!s} vs {1!s}'.format(xaxis, item), fontsize=12)
                        
                        plt.legend(loc='best', fontsize=10)
                        
                        plt.xlabel('Iteration Count')
                        plt.xticks(fontsize=10, rotation=30)
                        
                        plt.ylabel(y_label)
                        plt.yticks(fontsize=10)
                        
                        plt.text(0.8, 0.1, text_str, transform=ax.transAxes, fontsize=10, bbox=props)
                        
                        plt.savefig("{0!s} vs {1!s} - {2!s}.png".format(xaxis, item, test_type))
                
                except Exception as e:
                    base_logger.error("Tearing down. Failed to plot graphs because : {0!s}".format(e))
            else:
                base_logger.error("No numerical data available to plot!")

        return

    def calcPerc(self, metric):
        """
        :param:metric: Parameter for which statistical percentile are being calculated
        :return:stats_dict: Dictionary containing values for SD, 95th, 90, 50 percentiles for metric
        """
        stats_dict = {}
        
        base_logger.info("Calculating Statistical percentages for {0!s}".format(metric))
        
        np_metric = self.df[metric].to_numpy()

        stats_dict['95'] = str((np.percentile(np_metric, 95)).round(decimals=2))
        base_logger.info("95 is {0!s}".format(stats_dict['95']))
        stats_dict['90'] = str((np.percentile(np_metric, 90)).round(decimals=2))
        base_logger.info("90 is {0!s}".format(stats_dict['90']))
        stats_dict['50'] = str((np.percentile(np_metric, 50)).round(decimals=2))
        base_logger.info("50 is {0!s}".format(stats_dict['50']))
        stats_dict['Std Dev'] = str((np.std(np_metric)).round(decimals=2))
        base_logger.info("SD is {0!s}".format(stats_dict['Std Dev']))

        return stats_dict











