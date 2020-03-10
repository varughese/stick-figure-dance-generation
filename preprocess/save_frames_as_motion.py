#!/usr/bin/env python
# coding: utf-8

# In[5]:


import os, pathlib, json
import numpy as np
from pathlib import Path
import os.path


# In[6]:


ROOT_DIR = "../densepose/txt/"
CATEGORIES = os.listdir(ROOT_DIR)
FRAME_DESCRIPTOR_LENGTH = len("_1234.json")


# In[7]:


def filename_to_id(filename):
    return filename[0:-FRAME_DESCRIPTOR_LENGTH]


# In[8]:


def filename_to_frame_no(filename):
    # lWfg9CNg-uE_123_FRAMENO.json
    # Split on _ -> [lWfg9CNg-uE, 123, FRAMENO.json]
    # Get last element, and then read convert FRAMENO to int
    return int(filename.split("_")[-1].split(".")[0])


# In[10]:

def create_index():
    index = {}
    for category in CATEGORIES:
        DANCE_DIR = "{}{}/".format(ROOT_DIR, category)
        filenames = os.listdir(DANCE_DIR)
        filenames.sort()
        for filename in filenames:
            if category not in index:
                index[category] = {}
            dance_id = filename_to_id(filename)
            frame = filename_to_frame_no(filename)
            if dance_id not in index[category]:
                index[category][dance_id] = [1, -1]
            index[category][dance_id][1] = frame
    return index


# In[12]:





# In[21]:

index = create_index()
output = []
for category in index.keys():
    for dance_id in index[category].keys():
        frames = index[category][dance_id][1]
        output.append([category, dance_id, frames])
        
# In[27]:

def frames_to_motion(category, dance_id, frames):
    motion = []
    for frame in range(1, frames):
        current_frame_path = "{}{}/{}_{:04d}.json".format(ROOT_DIR, category, dance_id, frame)
        if os.path.exists(current_frame_path): 
            with open(current_frame_path) as f:
                data = json.load(f)
            motion.append(data)
        else:
            print("ERROR - Missing {}".format(current_frame_path))
    return motion


# In[34]:



counter = 0
total = len(output)
for d in output:
    [category, dance_id, frames] = d 
    motion = frames_to_motion(category, dance_id, frames)
    dir_path = '../densepose/full/{}'.format(category)
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    file_path = '{}/{}.json'.format(dir_path, dance_id)
    counter += 1
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as f:
            json.dump(motion, f)
            f.close()
        print('{}_{} {}/{}'.format(category, dance_id, counter, total))
    else:
        print('{}_{} Exists'.format(category, dance_id, counter, total))


# In[ ]:




