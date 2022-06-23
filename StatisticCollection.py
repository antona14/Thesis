#!/usr/bin/env python
# coding: utf-8

# In[2]:


from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.statistics.traces.generic.log import case_statistics
from pm4py.statistics.sojourn_time.log import get as soj_time_get
from collections import Counter
from collections import defaultdict
import statistics as stats
import pm4py
import pandas as pd
from prettytable import PrettyTable
# from tabulate import tabulate
import json
import numpy as np
from scipy.stats import norm
from scipy.stats import poisson


# In[3]:


def calcFrequency(log3A):
    # Initializing
    totalDays = len(log3A)
    totalFreq = {}
    averageFreq = {}
    DayFreq = []
    total = 0

    for i in range(len(log3A)):
        daylist = []
        for k in range(len(log3A[i])):
            daylist.append(log3A[i][k]['concept:name'])

    #     using Counter to find frequency of elements
        activityFrequency = dict(Counter(daylist))
#         print("Frequency for day", i+1, ":", activityFrequency)
        DayFreq.append(activityFrequency)        
        
        for key, value in activityFrequency.items():
            totalFreq.setdefault(key, 0)
            totalFreq[key] += value
            total += value

#     print("TOTAL FREQUENCY:", totalFreq)


    for key, values in totalFreq.items():
#         print(key, "-> ", end="")
#         print(values, "times")
#         print("AVERAGE per day:", values, "/", totalDays, "=", values/totalDays)
#         print("NORMALIZED:     ", values, "/", total, "=", values/total)
        average = values/totalDays
        averageFreq[key] = average
#         print("")
        
#     print("---------------------------------------------------------------------------")
    
#     return totalFreq, averageFreq, DayFreq
    return averageFreq, DayFreq


# In[4]:


def fitnessOfFreq(log3A, testLog):
    averageFreq, dayFreq = calcFrequency(log3A)
    fitRes = []
#     print(averageFreq)
    activityFreqPerDay = defaultdict(list)
    for day in dayFreq:
        for key in day:
            activityFreqPerDay[key].append(day[key])
    

    for i in range(len(testLog)):
        day_activity = []
        freq_cc_result = {key:[] for key in averageFreq.keys()}
    
        for case in testLog[i]:
            day_activity.append(case['concept:name']) 
            activityFreq = dict(Counter(day_activity))
            
#         print('Day', i)       

#         print(activityFreq)


        freq_cc_result = defaultdict(list)
        for activity in activityFreqPerDay:
            countMost = max(activityFreqPerDay[activity], key=activityFreqPerDay[activity].count)
#             countMost = averageFreq[activity]
            y = poisson.pmf(k = countMost, mu = np.mean(activityFreqPerDay[activity]))
            if activity in activityFreq.keys():
#                 print(activity,activityFreq [activity])
#                 print(poisson.pmf(k = activityFreq [activity], mu = np.mean(activityFreqPerDay[activity])))
#                 print("countMost", countMost)
#                 print(np.mean(activityFreqPerDay[activity]))
#                 print("countMost", poisson.pmf(k = countMost, mu = np.mean(activityFreqPerDay[activity])))
#                 print(1/((activityFreq[key]-np.mean(activityFreqPerDay[activity]))**2+1))

                freq_cc_result[activity] = min((poisson.pmf(k = activityFreq [activity], mu = np.mean(activityFreqPerDay[activity]))/
                                                poisson.pmf(k = countMost, mu = np.mean(activityFreqPerDay[activity])))
                                               , 1)
            else:
                freq_cc_result[activity] = None
        fitRes.append(freq_cc_result)
#         print(freq_cc_result)
#         print('-------------')    

    
    return fitRes


# In[5]:


def get_freq_fitness(log, testLog):
    ccFitRes = fitnessOfFreq(log, testLog)
    result = []
    
    for day in ccFitRes:
        res = 0
        counta = 0
        for activity, value in day.items():
            if value is not None:
                res += value
                counta += 1
            else:
                continue
        res = res/counta
#         print(res)
        result.append(round(res, 3))
    return result


# In[6]:


def get_activity_duration(log):
    soj_time = soj_time_get.apply(log, parameters={soj_time_get.Parameters.TIMESTAMP_KEY: "time:timestamp", soj_time_get.Parameters.START_TIMESTAMP_KEY: "start_time"})
    return soj_time


# In[7]:


def get_dur_stdev(log):
    attr_list = pm4py.statistics.attributes.log.get.get_attribute_values(log, attribute_key="concept:name")
    d = {}
    for act in attr_list.keys():
        d[act] = []
    for trace in log:
        for event in trace:
            end = event.get("time:timestamp")
            start = event.get("start_time")
            duration = end - start    
            duration_in_s = duration.total_seconds() 
            d[event.get("concept:name")].append(duration_in_s)
    stdev = {}
    for activity, values in d.items():
        mm = stats.stdev(values)
        stdev[activity] = mm
    return(stdev)


# In[8]:


def get_activity_count(log):
    averageFreq, dayFreq = calcFrequency(log)
#     print(dayFreq)
    activityFreqPerDay = defaultdict(list)
    for day in dayFreq:
        for key in day:
            activityFreqPerDay[key].append(day[key])
#     print(activityFreqPerDay)
    return activityFreqPerDay


# In[9]:


def get_duration_fitness(log, testLog):
    # this is my ground truth
    
    result = []
        
    meansduration = get_activity_duration(log)  
    stdevsduration = get_dur_stdev(log)

    for trace in testLog:
        ddict = {}
        fitness = []
        ActivityDurationToday = defaultdict(list)
        for event in trace:
            end = event.get("time:timestamp")
            start = event.get("start_time")
            duration = end - start    
            duration_in_s = duration.total_seconds() 

            if event.get("concept:name") in ddict:
                ddict[event.get("concept:name")].append(duration_in_s) 
            else: ddict[event.get("concept:name")] = [duration_in_s]
#         print(ddict.items())
        for activity, values in ddict.items():
            dnorm = meansduration.get(activity)

            dstdev = stdevsduration.get(activity)
            
            for value in values:
                f = norm.pdf(value, loc = dnorm , scale = dstdev)
                g = norm.pdf(dnorm, loc = dnorm , scale = dstdev)
                ActivityDurationToday[activity].append(round(f/g,3))
#             fitness.append(round(f/g,3))
#         result[trace.attributes.get("concept:name")] = fitness
        result.append(ActivityDurationToday)    

#     tot = []
#     for t in result.values():
#         # print("Trace fitness: ", sum(t)/len(t))   
#         tot.append(sum(t)/len(t))
#     # print("Total fitness: ", sum(tot)/len(logTest))


    return result 


# In[10]:


def get_duration_fitness_min(log, testLog):
    ccDuraRes = get_duration_fitness(log, testLog)
    result = []
    for day in ccDuraRes:
        minRes = {}
        for activity, values in day.items():
            minRes[activity] = min(values)
        result.append(minRes)
#         print(minRes)

    return result


# In[11]:


def get_duration_fitness_mean(log, testLog):
    ccDuraRes = get_duration_fitness(log, testLog)
    result = []
    for day in ccDuraRes:
        meanRes = {}
        for activity, values in day.items():
            meanRes[activity] = np.mean(values)
        result.append(meanRes)
#         print(minRes)

    return result


# In[12]:


def get_duration_fitness_final_min(log, testLog):
    minRes = get_duration_fitness_min(log, testLog)
    result = []
    
    for day in minRes:
        res = 1
        for activity, value in day.items():
            res = min(res, value)
        result.append(res)
#         print(res)
    return result


# In[13]:


def get_duration_fitness_final_mean(log, testLog):
    meanRes = get_duration_fitness_mean(log, testLog)
    result = []
    
    for day in meanRes:
        res = 0
        for activity, value in day.items():
            res += value
        res = res/len(day.items())
#         print(res)
        result.append(res)
    return result


# In[14]:


def get_duration_fitness_final_min_mean(log, testLog):
    meanRes = get_duration_fitness_mean(log, testLog)
    result = []
    
    for day in meanRes:
        res = 1
        for activity, value in day.items():
            res = min(res, value)
        result.append(round(res,3))
#         print(res)
    return result


# In[15]:


def get_duration_fitnessV2(log, testLog):
    # this is my ground truth
    
    result = []
        
    meansduration = get_activity_duration(log)  
    stdevsduration = get_dur_stdev(log)

    for trace in testLog:
        ddict = {}
        fitness = []
        ActivityDurationToday = defaultdict(list)
        for event in trace:
            end = event.get("time:timestamp")
            start = event.get("start_time")
            duration = end - start    
            duration_in_s = duration.total_seconds() 

            if event.get("concept:name") in ddict:
                ddict[event.get("concept:name")].append(duration_in_s) 
            else: ddict[event.get("concept:name")] = [duration_in_s]
#         print(ddict.items())
        for activity, values in ddict.items():
            dnorm = meansduration.get(activity)

            dstdev = stdevsduration.get(activity)
            
            ccmean = stats.mean(values)
            f = norm.pdf(ccmean, loc = dnorm , scale = dstdev)
            g = norm.pdf(dnorm, loc = dnorm , scale = dstdev)
            ActivityDurationToday[activity].append(round(f/g,3))
#             fitness.append(round(f/g,3))
#         result[trace.attributes.get("concept:name")] = fitness
        result.append(ActivityDurationToday)    

#     tot = []
#     for t in result.values():
#         # print("Trace fitness: ", sum(t)/len(t))   
#         tot.append(sum(t)/len(t))
#     # print("Total fitness: ", sum(tot)/len(logTest))


    return result 


# In[16]:


# log = xes_importer.apply("NightRoutine3AMay.xes")
# testlog3A = xes_importer.apply("NightRoutine3ACC.xes")
# testlog = xes_importer.apply("NightRoutine3BMay.xes")


# In[17]:


# get_duration_fitness_final_mean(log, testlog)


# In[18]:


# get_duration_fitness_final_mean(log, testlog3A)


# In[19]:


# get_freq_fitness(log, testlog3A)


# In[20]:


# get_freq_fitness(log, testlog)

