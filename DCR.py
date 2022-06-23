#!/usr/bin/env python
# coding: utf-8

# In[46]:


from pm4py.objects.log.importer.xes import importer as xes_importer
import subprocess
import csv
import sys
import os
from json import loads
import json
from dicttoxml import dicttoxml

import xml.dom.minidom as xdm
import sys

import pandas as pd
import glob, os

import xmltodict
from collections import OrderedDict
from ordered_set import OrderedSet

#Anton
from statistics import mean
from collections import Counter


# In[13]:


def defineID(json_model):
    with open(json_model, 'r') as jf:
        load_dict = loads(jf.read())
        dict_list = load_dict['Relation']
        activities_list = []

        for item in dict_list:
            if item['source'] not in activities_list:
                activities_list.append(item['source'])
            if item['target'] not in activities_list:
                activities_list.append(item['target'])

        value_list = ['activity%d' % i for i in range(len(activities_list))]
        return activities_list, value_list


# In[91]:


def json2xml(json_model, xml_model, value_list, activities_list, activities_dict):
    
    activities_dict = activities_dict
    
    with open(json_model, 'r') as json_file:
        load_dict = loads(json_file.read())
        #print(load_dict)
        #item_func = 
        #xml = dicttoxml(load_dict, custom_root=)
        dict_list = load_dict['Relation']
        out_xml = xdm.Document()
        root = out_xml.createElement('dcrgraph')
        out_xml.appendChild(root)
        subroot = out_xml.createElement('specification')
        root.appendChild(subroot)
        
        # RESOURCE: EVENT, LABEL, LABELMAPPING, CONSTRAINTS
        root_res = out_xml.createElement('resources')
        subroot.appendChild(root_res)
        root_events = out_xml.createElement('events')
        root_res.appendChild(root_events) 
        root_labels = out_xml.createElement('labels')
        root_res.appendChild(root_labels)
        root_labelMap = out_xml.createElement('labelMappings')
        root_res.appendChild(root_labelMap)  
        root_expressions = out_xml.createElement('expressions')
        root_res.appendChild(root_expressions)  
        
        # CONSTRAINTS: CONDITIONS, RESPONSES, INCLUDES, EXCLUDES
        root_constraints = out_xml.createElement('constraints')
        subroot.appendChild(root_constraints)
        
#         activities_list = []
    
#         for item in dict_list:
#             if item['source'] not in activities_list:
#                 activities_list.append(item['source'])
#             if item['target'] not in activities_list:
#                 activities_list.append(item['target'])
#         value_list = ['activtiy%d' % i for i in range(len(activities_list))]
#         activities_dict = dict(zip(activities_list, value_list))
        #print(type(activities_dict))
        
        for activity in value_list:
            node_item = out_xml.createElement('event')
            node_item.setAttribute('id', activity)
            root_events.appendChild(node_item)
        
        # label
        for activity in activities_list:
            node_item = out_xml.createElement('label')
            node_item.setAttribute('id', activity)
            root_labels.appendChild(node_item)

        # label Mapping
        for item in activities_dict.items():
            #print(item)
            node_item = out_xml.createElement('labelMapping')
            node_item.setAttribute('eventId', item[1])
            node_item.setAttribute('labelId', item[0])
            root_labelMap.appendChild(node_item)
            
        # expressions
        for i in range(2):
            node_item = out_xml.createElement('expression')
            node_item.setAttribute('id', 'null')
            node_item.setAttribute('value', 'null = null')
            root_expressions.appendChild(node_item)
        
        # get all the relation between items, and create node
        relation_list = []
        
        for dict_item in dict_list:
            if dict_item['type'] not in relation_list:
                relation_list.append(dict_item['type'])
        
        for relation in relation_list:
            node_item = out_xml.createElement(relation+'s')
            for dict_item in dict_list:
                if dict_item['type'] == relation:
                    subnode_item = out_xml.createElement(dict_item['type'])
                    #node_item.setAttribute('sourceId', dict_item['source'])
                    subnode_item.setAttribute('sourceId', activities_dict.get(dict_item['source']))
                    subnode_item.setAttribute('targetId', activities_dict.get(dict_item['target']))
                    node_item.appendChild(subnode_item)
            root_constraints.appendChild(node_item)
        
        # RUNTIMEL: MARKING: GLOBALSTORE, EXECUTED, INCLUDED, PENDINGRESPONSES
        subroot = out_xml.createElement('runtime')
        root.appendChild(subroot)
        
        root_mark = out_xml.createElement('marking')
        subroot.appendChild(root_mark)
        root_mark.appendChild(out_xml.createElement('globalStore'))
        root_mark.appendChild(out_xml.createElement('executed'))
        root_included = out_xml.createElement('included')
        root_mark.appendChild(root_included)
        for activity in value_list:
            #root_included.appendChild(out_xml.createElement('event').setAttribute('id', activity))
            node_item = out_xml.createElement('event')
            node_item.setAttribute('id', activity)
            root_included.appendChild(node_item)
            
        root_mark.appendChild(out_xml.createElement('pendingResponses'))
        
        
        
        #file_output = open('xmlTest.xml', 'w')
        # Check the root value, dom.toprettyxml() / toxml
#         print(out_xml.toprettyxml(indent = '   '))
        
        with open(xml_model, 'w') as f:
            out_xml.writexml(writer=f, indent='    ', addindent='\t', newl='\n')
            #print(out_xml.toprettyxml(indent='   '))
            f.close()
        #file_output.close()


# In[93]:


def dcrDiscovery(path_logA):
    print('DCR DISCOVERY...')
    subprocess.call(['java', '-jar', 'dcr-discovery.jar', path_logA, "dcrModel.JSON"])
    print('Creat model at: ', os.getcwd()+'/dcrModel.JSON')
    
    print('Convert json to xml format...')
    activities_list, value_list = defineID(os.getcwd()+'/dcrModel.JSON')
    activities_dict = dict(zip(activities_list, value_list))
    print(value_list, activities_list)

    json2xml(os.getcwd()+'/dcrModel.JSON', 'dcrModel.xml', value_list, activities_list, activities_dict)
    print('Create xml model at: ', os.getcwd()+'/dcrModel.xml')
    return activities_dict


# In[38]:


def formatTransferEL(input_file, activities_dict):
    dom = xdm.parse(input_file)
#     print('11')
#     print(input_file.split('/')[-1].split('.'))
    output_file = input_file.split('/')[-1].split('.')[0]+'DCRCC.xml'
#     print('22')
    print(output_file)

    
    # MODIFY THE SUBLABEL AS ATTRIBUTES
    events = dom.getElementsByTagName('event')
    
    for event in events:
        subevents = event.getElementsByTagName('int')
        for i in range(len(subevents)):
            key = subevents[i].attributes.getNamedItem("key").nodeValue
            value = subevents[i].attributes.getNamedItem("value").nodeValue
            event.setAttribute(key, value)

        subevents = event.getElementsByTagName('string')
        for i in range(len(subevents)):
            value = subevents[i].attributes.getNamedItem("value").nodeValue
            event_id = activities_dict.get(value)
            event.setAttribute('id', event_id)
            event.setAttribute('label', value)

        subevents = event.getElementsByTagName('date')
        for i in range(len(subevents)):
            key = subevents[i].attributes.getNamedItem("key").nodeValue
            value = subevents[i].attributes.getNamedItem("value").nodeValue
            event.setAttribute(key, value)
            
        subevents = event.getElementsByTagName('float')
        for i in range(len(subevents)):
            key = subevents[i].attributes.getNamedItem("key").nodeValue
            value = subevents[i].attributes.getNamedItem("value").nodeValue
            event.setAttribute(key, value)
    
    int_list = dom.getElementsByTagName('int')
    for single_int in int_list:
        single_int.parentNode.removeChild(single_int)

    string_list = dom.getElementsByTagName('string')
    for single_string in string_list:
        single_string.parentNode.removeChild(single_string)

    date_list = dom.getElementsByTagName('date')
    for single_date in date_list:
        single_date.parentNode.removeChild(single_date)
        
    float_list = dom.getElementsByTagName('float')
    for single_date in float_list:
        single_date.parentNode.removeChild(single_date)
        
        

    
    output_file.replace('\n','')
    with open(output_file, 'w') as f:
        dom.writexml(writer=f, indent='', addindent='', newl='')
        #print(out_xml.toprettyxml(indent='   '))
        #print('SUCCESS')
        print('____SUCCESS_____')
        f.close()
        
    return output_file


# In[56]:


class Trace:
    """
    A class used to handle log traces executed from an DCR model
    
    ...
    
    Attributes
    ----------
    _trace : OrderedDict
        a dictionary containing the trace log
    
    _events : list
        a list containing only the events from the trace log
    
    Methods
    -------
    extract_events()
        extracts all the events from the raw log in sequence
    
    """
    
    def __init__(self, trace):
        """
        Parameters
        ----------
        _trace : OrderedDict
            a dicitonary containing the trace log
        
        """
        
        self._trace = trace
        self._events = []

    
    # Extracting events
    def extract_events(self):
        """
        extracts all event containers from the parsed XML log and appends then into sequence.
        does not provide return value, method manipulates object attributes in-place
        
        """
        
#         for log in self._trace['log']['trace']['event']:

        for log in self._trace['trace']['event']:
            #print(log)
            self._events.append(log)


# In[57]:


class ProcessModel:
    """
    A class for creating a model object of a DCR model.
    
    ...
    
    Attributes 
    ----------
    _model : OrderedDict
        dictionary representing the DCR graph model
    
    _relations : dict
        dictionary containing combinations of activity relations as keys, together with corresponding 
        constraints as values. excludes all relations which are governed by data input
    
    _time : dict
        dictionary containing time-dependent relations, e.g constraints with delay or deadline control
        relation as key and temporal data as value
    
    _expressions : dict
        dictionary containing information of data related choices and input, together with corresponding 
        link/action ID. data guard as key, with correpsonding link/mapping ID as value
        
    _expression_relations : dict
        dictionary containing information of data-dependant constraints: link/mapping ID as key, 
        activity relation and affecting constraint as value
    
    _subevents : dict
        dictionary containing all event ID's of nested events inside a subprocess/nesting process as keys,
        with the corresponding subprocess/nesting ID as values
        
    _subprocess : dict
        dicitonary containing all subprocess/nesting ID's as keys with corresponding nested 
        subevents ID's as values
        
    _activities : dict
        dictionary containing all activities as keys and their current state (included, pending, executed) 
        as values
        
    _included : list
        list containing all activities which are included according to the model
        
    _pending = list
        list containing all activities which are pending according to the model
        
    _executed = list
        list containing all activities which are executed according to the model
        
    Methods
    -------
    extract_relations()
        extracts all the relations comprised by the constraints of the DCR model
        
    extract_nested_activities()
        extracts information on nested/subprocess types and activities 
        
    extract_activities()
        extracts all activity ID's and append tuple of state
        
    extract_expressions()
        extracts all data-dependent relations, data gaurds and their corresponding link/mapping ID
        
    extract_markings()
        extracts the initial state of the activities corresponding to the model
        
    extract_all()
        performs all above methods in sequence

    """
    
    def __init__(self, model):
        """
        Parameters
        ----------
        model : OrderedDict()
            a dictionary representing the DCR graph model
        """
        
        self._model = model
        self._relations = {}
        self._time = {}
        self._expressions = {}
        self._expression_relations = {}
        self._subevents = {}
        self._subprocess = {}
        self._activities = {}
        self._included = []
        self._pending = []
        self._executed = []
                
    # method for extracting all the relations between activities and the corresponding constraints
    def extract_relations(self):
        """
        method for extracting the relations between activities comprised by the constraints of the DCR model.
        does not provide return value, method manipulates object attributes in-place
        """
        
        # traverse the dictionary
        for events in self._model.get('dcrgraph').get('specification').get('constraints').values():    
            if events is not None: 
                # print(type(events))
                # iterate through all constraints and relations
                # cast constraints to lists in order to handle multiple constraints per relation
                for constraint, relation in events.items(): 
#                     print('constraint   '+constraint+'\n')
#                     print(relation)
#                     print('___________')
                    if type(relation) != list: 
                            relation = [relation]
                            
                    for i in range(0, len(relation)):
                        # fetch all data-dependent relations
                        if '@expressionId' in relation[i].keys():
                            if relation[i]['@expressionId'] not in self._expression_relations.items():

                                self._expression_relations[relation[i]['@expressionId']] = {
                                    (relation[i]['@sourceId'], relation[i]['@targetId']) : constraint} 
                        
                        # fetch all non-data dependent relations 
                        else:
                            if (relation[i]['@sourceId'], relation[i]['@targetId']) not in self._relations.keys():
                                self._relations[relation[i]['@sourceId'], 
                                                relation[i]['@targetId']] = [constraint]
                            else:
                                # append constraints to existing relations

                                self._relations[(relation[i]['@sourceId'], 
                                                 relation[i]['@targetId'])].append(constraint)

                        # fetch data on constraints with delays/deadlines
#                         if relation[i]['@time'] != '':
#                             self._time[(relation[i]['@sourceId'], 
#                                         relation[i]['@targetId'])] = relation[i]['@time']

                        
    
    # method for fetching nested events and its subprocesses
    def extract_nested_activities(self):
        """
        method for extracting information on nested/subprocess types and activities.
        does not provide return value, method manipulates object attributes in-place
        """
        
        # traverse the dicitonary
        for events in self._model.get('dcrgraph').get('specification').get('resources').get('events').values():
            for subprocess in events:

                # init nesting/subprocesses type
                if '@type' in subprocess.keys():                    
                    if subprocess['@type'] not in self._subevents.keys():
                        self._subevents[subprocess['@type']] = {}
                        self._subprocess[subprocess['@type']] = {}
                        self._subprocess[subprocess['@type']][subprocess['@id']] = []
                    else:
                        self._subprocess[subprocess['@type']][subprocess['@id']] = []
                    
                    # iterate through all nested activities and fetch both activity ID together
                    # with nesting ID and nesting ID together with activity ID into dictionaries
                    for subevent in subprocess.get('event'):
                        
                        self._subprocess[subprocess['@type']][subprocess['@id']].append(subevent['@id'])
                        self._subevents[subprocess['@type']][subevent['@id']] = subprocess['@id']
                        
        
    
    # method for fetching activity relation data guards
    def extract_expressions(self):
        """
        method for extracting data-dependent relations, data gaurds and their corresponding link/mapping ID.
        does not provide return value, method manipulates object attributes in-place
        """
        
        expression = self._model.get('dcrgraph').get('specification').get('resources').get('expressions').get('expression')
        # get data for each activity and sanitize format
        for exp in expression:
            exp = list(exp.values())
            e = exp[1].split('=')
            e[0] = e[0].strip()
            e[1] = e[1].strip()
            if (e[0],e[1]) not in self._expressions.keys():
                self._expressions[(e[0],e[1])] = [exp[0]]
            else:
                self._expressions[(e[0],e[1])].append(exp[0])
            
            
    # method for fetching all the activities and assigning booleans for include, pending and extracted in order
    # to keep track of activity state. all states set to false initially
    def extract_activities(self):
        """
        method for extracting activity ID's and append tuple of state.
        does not provide return value, method manipulates object attributes in-place
        """
        
        activity = self._model.get('dcrgraph').get('specification').get('resources').get('labelMappings')
        for key, value in activity.items():
            n = len(value)
            for i in range(0, n):
                self._activities[value[i]['@eventId']] = [False, False, False]
        
    
    # method for fetching initial markings from the dcr-model
    def extract_markings(self):
        """
        method for extracting the initial state of the activities corresponding to the model.
        does not provide return value, method manipulates object attributes in-place
        """
        
        included = self._model.get('dcrgraph').get('runtime').get('marking').get('included')
        pending = self._model.get('dcrgraph').get('runtime').get('marking').get('pendingResponses')
        executed = self._model.get('dcrgraph').get('runtime').get('marking').get('executed')
        
        if included is not None:
            events = included.get('event')
            for event in events:
                self._included.append(event['@id'])
        
        if pending is not None:
            events = pending.get('event')
            for event in events:
                self._pending.append(event['@id'])
        
        if executed is not None:
            events = executed.get('event')
            for event in events:
                self._executed.append(event['@id'])
     
            
    def extract_all(self):
        """
        performs all above extracting methods in sequence.
        does not provide return value, method manipulates object attributes in-place
        """
        
        self.extract_relations()
        self.extract_nested_activities()
        self.extract_activities()
        self.extract_expressions()
        self.extract_markings()


# In[58]:


class Conformance:
    """ 
    A class used to perform check conformance between a DCR model and DCR log.
    Alogrithm dea is based on rule-based conformance checking and trace replay. 
    Conformity of a trace is checked by replaying a trace on a model while updating model state based on
    active constraints.

    ...

    Attributes
    ----------
   _trace_events : dict
       dictionary containing traces from a Trace class object

    _model_relations : dict
        dictionary containing relations from a ProcessMining class object

    _model_activities : dict
        dictionary containing activities from a ProcessMining class object

    _model_time : dict
        dictionary containing time dependent relations from a ProcessMining class object

    _model_expressions : dict
        dictionary containing data gaurd information from a ProcessMining class object

    _model_expression_relations : dict
        dictionary containing data dependent relations and mappings from a ProcessMining class object

    _model_subevents : dict
        dictionary containing events nested in a subprocess/nesting from a ProcessMining class object

    _model_subprocess : dict
        dictionary containing subprocesses/nestings with corresponding nested events, 
        from a ProcessMining class object

    _model_included : list
        dictionary containing initial included events from a ProcessMining class object

    _model_pending : list
        dictionary containing initial pending events from a ProcessMining class object

    _model_executed : list
        dictionary containing initial excluded events from a ProcessMining class object

    _isExecuted : OrderedSet
        set containing executed events, added to set in order

    _isIncluded : OrderedSet
        set containing included events, added to set in order

    _isPending : OrderedSet
        set containing pending events, added to set in order

    _isExcluded : set
        set containing excluded events

    _violations : dict
        dictionary containing violated activities and the violated constraint

    _isConform : bool
        boolean indicating if the replayed trace is conform or not
            True = Conform Trace
            False = Violating Trace

    Methods
    -------
    rule_checking(event, _id)
        method for handling data-dependent relations and checking their corresponding constraint rule

    check_expressions(trace)
        method for checking if a data-dependant activity has been activated and should be included

    check_include_rule(trace, relation)
        method for handling the include constraint

    check_exclude_rule(trace, relation)
        method for handling the exclude constraint

    check_response_rule(trace, relation)
        method for handling the response constraint

    check_condition_rule(trace, relation)
        method for handling the condition constraint

    trace_replay()
        method for conducting trace replay of log onto model. returns (1) lists representing the 
        state of the model after replay, (2) if log conformity is true or false
    """
    
    def __init__(self, trace, pm): 
        """
        Parameters
        ----------
        trace : Trace object (OrderedDict)
            dictionary containing a trace from a DCR model in from of a Trace class object
        
        pm : ProcessMining object (OrderedDict)
            dictionary containing a DCR model in form of a ProcessMining class object
        """
        
        # fetching trace data
        self._trace_events = trace._events
        
        # fetching model data
        self._model_relations = pm._relations
        self._model_activities = pm._activities
        self._model_time = pm._time
        self._model_expressions = pm._expressions
        self._model_expression_relations = pm._expression_relations
        self._model_subevents = pm._subevents
        self._model_subprocess = pm._subprocess
        self._model_included = pm._included
        self._model_pending = pm._pending
        self._model_executed = pm._executed
        
        #initializing variables
        self._isExecuted = OrderedSet()
        self._isIncluded = OrderedSet()
        self._isPending = OrderedSet()
        self._isExcluded = set()
        
        self._violations = {}
        self._isConform = False 
        
        
    def rule_checking(self, trace_event, _id):
        """
        method for handling data-dependent relations and checking their corresponding constraint rule.
        does not provide return value, method manipulates object attributes in-place
        
        Parameters
        ----------
        trace_event : Trace object (OrderedDict)
            the current data-dependent activity which is executed and evaluated
        
        _id : list
            list of mapping ID's which represents a relation between two activities and its constraint
            
        """
        for mapFromRule in _id:
            for mapToRule, relations in self._model_expression_relations.items():
                if mapFromRule == mapToRule:
                    for relation, constraint in relations.items():
                        
                        
                        self._isExecuted.add(relation[0])
                        self._model_activities[relation[0]][2] = True
                        
                        # handling include rule    
                        if (relation[0] in self._isIncluded and 
                            'include' == constraint and trace_event['@id'] in self._isExecuted):
                            self._isIncluded.add(relation[1])
                            self._model_activities[relation[1]][0] = True
                            self._isExcluded.discard(relation[1])
                        
                        # handling exclude rule
                        if (relation[0] in self._isIncluded and 'exclude' == constraint and 
                            trace_event['@id'] in self._isExecuted):
                            self._model_activities[relation[1]][0] = False
                            self._model_activities[relation[1]][1] = False
                            self._isIncluded.discard(relation[1])
                            self._isPending.discard(relation[1])
                            self._isExcluded.add(relation[1])
                        
                            
                        # handling response rule    
                        if (relation[0] in self._isExecuted and 
                            relation[1] in self._isIncluded and 'response' == constraint):
                            
                            self._model_activities[relation[1]][1] = True
                            self._isPending.add(relation[1])
                        
                        # handling condition rule
                        if (relation[1] in self._isIncluded and 'condition' == constraint):

                            try:
                                idx = list(self._isExecuted).index(trace_event['@id'])
                                if relation[0] not in self._isExecuted[:idx]:
                                    self._violations[trace_event['@id']] = constraint
                            except:
                                pass
                        
                        # add activity relation to relation dictionary
                        if relation not in self._model_relations.keys():
                            self._model_relations[relation] = [constraint]
                        else:
                            self._model_relations[relation].append(constraint)
       
    
    def check_expressions(self, trace_event):
        """
        method for checking if a data-dependant activity has been activated and should be included.
        does not provide return value, method manipulates object attributes in-place
        
        Parameters
        ----------
        trace_event : Trace object (OrderedDict)
            dictionary containing information regarding the current event
        
        """
        
        events = self._model_expressions.items()
        for event in events: 
            if trace_event['@id'] == event[0][0]:
                if trace_event['@data'] == event[0][1]:
                    _id = event[1]
                    _id.sort()
                    self.rule_checking(trace_event,_id)
                    
            if trace_event['@id'] == event[0][1]:
                data = trace_event['@data']
                for data_source in self._trace_events:
                    if data_source['@id'] == event[0][0] and data == data_source['@data']:
                        _id = event[1]
                        _id.sort()
                        self.rule_checking(trace_event,_id)

    
    
    def check_include_rule(self, trace_event, relation):
        """
        method for handling the DCR inclusion constraint.
        a include b
        if activity a has been executed and has an include relation to b, b gets included.
        does not provide return value, method manipulates object attributes in-place
        
        Parameters
        ----------
        trace_event : Trace object (OrderedDict)
            dictionary containing information regarding the current event
        
        relation : tuple
            tuple of the relation related to the current evaluated trace_event
        """
        
        # Handling include rule
        #print(relation)[0]
        if (trace_event == relation[0] and trace_event in self._isExecuted):
            self._isIncluded.add(relation[1])
            self._model_activities[relation[1]][0] = True
            self._isExcluded.discard(relation[1])
            

            
    def check_response_rule(self, trace_event, relation):
        """
        method for handling the DCR response constraint.
        a response b
        if activity a has been executed and has a response relation to b, 
        b is pending a response iff b is included.
        does not provide return value, method manipulates object attributes in-place
        
        Parameters
        ----------
        trace_event : Trace object (OrderedDict)
            dictionary containing information regarding the current event
        
        relation : tuple
            tuple of the relation related to the current evaluated trace_event
        """
        
        # Handling response rule
        if (trace_event == relation[0] and trace_event in self._isExecuted and relation[1] in self._isIncluded):

            self._model_activities[relation[1]][1] = True
            self._isPending.add(relation[1])

            
    def check_condition_rule(self, trace_event, relation):
        """
        method for handling the DCR condition constraint.
        a condition b
        if activity b has been executed and has an ingoing condition relation from a, 
        a must have been included and executed prior to b.
        does not provide return value, method manipulates object attributes in-place
        
        Parameters
        ----------
        trace_event : Trace object (OrderedDict)
            dictionary containing information regarding the current event
        
        relation : tuple
            tuple of the relation related to the current evaluated trace_event
        """
        # Handling condition rule
        if (trace_event == relation[1]):
            try:
                idx = list(self._isExecuted).index(trace_event)
                if relation[0] not in self._isExecuted[:idx]:
                    self._violations[trace_event] = 'ingoing condition violated'
            except:
                pass
            

    def check_exclude_rule(self, trace_event, relation):
        """
        method for handling the DCR condition constraint.
        a exclude b
        if activity a has been executed and has an exclude relation to b, 
        b is excluded.
        does not provide return value, method manipulates object attributes in-place
        
        Parameters
        ----------
        trace_event : Trace object (OrderedDict)
            dictionary containing information regarding the current event
        
        relation : tuple
            tuple of the relation related to the current evaluated trace_event
        """
        
        # Handling exclude rule
        if (trace_event == relation[0] and trace_event in self._isExecuted):
            self._model_activities[relation[1]][0] = False
            self._model_activities[relation[1]][1] = False
            self._isIncluded.discard(relation[1])
            self._isExcluded.add(relation[1])
            self._isPending.discard(relation[1])        
    
    def trace_replay(self):
        """
        method for conducting trace replay of a DCR trace onto the desired DCR model.
        
        Attributes
        ----------
        nested_events : set
            set comprised of all nested events
        
        nesting_IDs : set
            set comprised of all subprocess/nestings
        
        Returns
        -------
        isIncluded : list
            list of all included activities after a trace replay
            
        isPending : list
            list of all pending activities after a trace replay
            
        isExecuted : list
            list of all executed activities after a trace replay
            
        isExcluded : list
            list of all excluded activities after a trace replay
            
        isConform : bool
            boolean indicating wheter the trace is conform or not
                True = Conform Trace
                False = Violating Trace
        
        """
        
        nested_events = set()
        nesting_IDs = set()
        
        # extract all nested event ID's and nesting ID's
        temp_nested_events = list(self._model_subevents.values())
        for events in temp_nested_events:
            for event in events.values():
                nesting_IDs.add(event)
            for events in events.keys():
                nested_events.add(event)
        
        # iterate through trace_events
        for trace_event in self._trace_events:
            
            # getting all included activities which are subprocesses/nesting etc
            for pending_event in self._isPending:
                if pending_event in nesting_IDs:
                    for subevent in list(self._model_subevents.values()):
                        for key, value in subevent.items():
                            if pending_event == value and pending_event in self._isIncluded:
                                if key in self._model_included or key in self._isIncluded: 
                                    self._isIncluded.add(key)
                                    self._model_activities[key][0] = True
                                else:
                                    self._isExcluded.add(key)

            # find all included activities in the model which are not nested and add to inclusion list
            #print(self._model_included)
            for included_event in self._model_included:
#                 print(included_event)
#                 print(trace_event['@id'])
#                 print(nested_events)
#                 print('------')
                
                if trace_event['@id'] == included_event and trace_event['@id'] not in nested_events:
#                     print('executed')
                    self._model_activities[trace_event['@id']][0] = True
                    self._isIncluded.add(trace_event['@id'])
                    
            
            # add trace_event to violating if excluded
            if trace_event['@id'] in self._isExcluded:
                self._violations[trace_event['@id']] = 'excluded activity executed'

            # add trace_event to list of executions if it exists in the model
            for model_event in self._model_activities:
                if trace_event['@id'] == model_event:
                    self._model_activities[trace_event['@id']][2] = True
                    self._model_activities[trace_event['@id']][1] = False
                    self._isExecuted.add(trace_event['@id'])
            
            
            if trace_event['@id'] in self._isIncluded:

            # check relation activity for current trace_event
                for relation in self._model_relations.items():
#                     print(relation)
                    # if relation exists
                    if trace_event['@id'] == relation[0][0]:

                        if 'include' in relation[1]:
                            self.check_include_rule(trace_event['@id'], relation[0])
                        if 'exclude' in relation[1]:
                            self.check_exclude_rule(trace_event['@id'], relation[0])
                        if 'response' in relation[1]:    
                            self.check_response_rule(trace_event['@id'], relation[0])
                        if 'condition' in relation[1]:
                            self.check_condition_rule(trace_event['@id'], relation[0])
                
                # handle data-dependent activity
                if '@data' in trace_event.keys():
                    self.check_expressions(trace_event)



            # replacing pending and included subprocesses with it's nested ID's
            temp_pending = list(self._isPending)
            for pending_event in temp_pending:
                cnt = 0

                for nesting_type, events in self._model_subevents.items(): 
                    for subevent, subprocess in events.items():

                        # handling nesting type subprocess and adding subevents if the whole process 
                        # has been included
                        if nesting_type == 'nesting' and subprocess == pending_event:
                            self._isPending.add(subevent)
                            self._isIncluded.add(subevent)
                            self._model_activities[subevent][0] = True
                            self._model_activities[subevent][1] = True
                        if nesting_type == 'subprocess' and trace_event['@id'] == subevent:
                            self._isPending.add(subprocess)

                        # counting activities executed in a specific subprocess/nesting
                        if (subprocess == pending_event) and subevent in self._isExecuted:
                            cnt = 1 + cnt

                    for process_type, events in self._model_subprocess.items():
                        for subprocess, subevents in events.items():
                            
                            # updating the state of the whole subprocess if all subprocess events have been
                            # executed and is not pending
                            if pending_event == subprocess:
                                if cnt == len(subevents):

                                    for relation in self._model_relations.items():

                                        if 'include' in relation[1]:
                                            self.check_include_rule(pending_event, relation[0])
                                        if 'exclude' in relation[1]:
                                            self.check_exclude_rule(pending_event, relation[0])
                                        if 'response' in relation[1]:    
                                            self.check_response_rule(pending_event, relation[0])
                                        if 'condition' in relation[1]:
                                            self.check_condition_rule(pending_event, relation[0])

                                    self._isExecuted.add(pending_event)
                                    self._model_activities[pending_event][2] = True

        
        # removing events from pending if they have been executed, else put them in violation list
        temp_pending2 = list(self._isPending)
        for pending_event in temp_pending2:
            if pending_event in self._isExecuted:
                if pending_event in self._isExcluded:
                    self._violations[pending_event] = 'executed but excluded'
                else:
                    self._isPending.discard(pending_event)
                    self._model_activities[pending_event][1] = False
            
            else:
                self._violations[pending_event] = 'is pending'
                
        # requirement for any trace to be conform is not having violations and no pending events
        if set(self._isIncluded) == (set(self._isExecuted)-set(self._isExcluded)) and (
            len(self._isPending) == 0) and len(self._violations) == 0:
            self._isConform = True

                
#         print(self._isIncluded)
#         print(self._isExecuted)
#         print(self._isExcluded)
#         print(self._isPending)
#         print(self._violations)
        return self._isConform, set(self._isIncluded), set(self._isPending), set(self._isExecuted), set(self._isExcluded)
    
    
   


# In[89]:


def mainCC(path_logA, path_logB):
    activities_dict = dcrDiscovery(path_logA)
    logB = formatTransferEL(path_logB, activities_dict)
    resCC = []
    
    fd = open('dcrModel.xml')
    xmlstr = fd.read()
    model = xmltodict.parse(xmlstr)
    
    with open(logB, 'r') as f:
        listf = f.read().split('</log>')[0]
        listf = ['<trace>'+trace for trace in listf.split('<trace>')]
    #     listf = ['<trace>'+trace for trace in f.read().split('<trace>')]
        for trace in listf[1:]:
            resCC.append(xmltodict.parse(trace))
    
    countRes = 0
    testCount = []
    for idx, log in enumerate(resCC):
        trace = Trace(log)
        trace.extract_events()

        pm = ProcessModel(model)
        pm.extract_all()

        cc = Conformance(trace, pm)
        cc.trace_replay()
        if cc._isConform:
            testCount.append(1)
            countRes += 1
#            print("Trace {} is conform: \n{}\n".format(idx, cc._isConform))
        else:
            testCount.append(0)
#            print("Trace {} is violating: \n{}\n".format(idx, cc._violations))

    countResults = Counter(testCount)
    
    return testCount
    
    print('-------------DCRFITNESS-------------')
#     print('AVERAGE FITNESS OF EVENTLOG: %s'% str(countRes/len(resCC)))
    print('AVERAGE FITNESS OF EVENTLOG: %s'% str(mean(testCount)))
    print('NUMBER OF VALID TRACES IN LOG: %s'% str(countResults[1]))
    print('NUMBER OF VIOLATING TRACES IN LOG: %s'% str(countResults[0]))
    
    
    
    

