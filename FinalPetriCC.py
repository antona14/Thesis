#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pm4py
from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay



# DISCOVERY INDUCTIVE AND HEURISTIC

def discovery_inductive(log):
    ind = inductive_miner.apply(log)
    return ind
def discovery_heuristic(log):
    heu = heuristics_miner.apply(log, parameters={heuristics_miner.Variants.CLASSIC.value.Parameters.DEPENDENCY_THRESH: 0.99})
    return heu


# CONFORMANCE

def conformance (logA, logB, alg, ccType):
    if(alg == "Inductive"):
        param = discovery_inductive(logA)
    elif(alg == "Heuristic"):
        param = discovery_heuristic(logA)
    else:
        raise Exception("Discovery algorithm not recognized")
    
    fitnessList = []
    
    if(ccType == "Alignment"):
        aligned_traces = alignments.apply_log(logB, param[0], param[1], param[2])
        for trace in aligned_traces:
            fitnessList.append(trace["fitness"])
    elif(ccType == "Replay"):
        replayed_traces = token_replay.apply(logB, param[0], param[1], param[2])
        for trace in replayed_traces:
            fitnessList.append(trace["trace_fitness"])        
    else:
        raise Exception("Conformance checking technique not recognized")
        
    return fitnessList

# conformance(log3a, log3b, "Inductive", "Alignment")


# In[8]:


#log3a = pm4py.read_xes('NightRoutine3AMay.xes')
#log3ap = pm4py.read_xes('NightRoutine3ACC.xes')
#log3b = pm4py.read_xes('NightRoutine3BMay.xes')
#
#print("Night 3A - Night 3B")
# print("Inductive, alignment:", conformance(log3a, log3b, "Inductive", "Alignment"))
# print("Inductive, replay:", conformance(log3a, log3b, "Inductive", "Replay"))
# print("Heuristic, alignment:", conformance(log3a, log3b, "Heuristic", "Alignment"))
# print("Heuristic, replay:", conformance(log3a, log3b, "Heuristic", "Replay"))

# conformance(log3a, log3b, "Inductive", "Alignment")
# conformance(log3a, log3b, "Inductive", "Replay")
# conformance(log3a, log3b, "Heuristic", "Alignment")
# conformance(log3a, log3b, "Heuristic", "Replay")

