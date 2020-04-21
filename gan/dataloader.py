import numpy as np
import json, codecs
import os
import torch
import torchvision
import matplotlib.pyplot as plt
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms
from torch.autograd.variable import Variable
from torch.utils.data import DataLoader
from tqdm import tqdm

# We preprocess'd the file names so we have a index with a list of all frames per dance id
FRAME_LIST_INDEX = './dance-frame-list.json'

# np.random.seed(0)
NUM_BODY_PARTS = 13
NUM_FEATURES = NUM_BODY_PARTS * 2
TOTAL_FRAMES = 250

# We have 250 frames. We are going to going to take the 17 body parts, 
# and turn it into 13 (remove eyes and ears). Then 13x2 (13 body parts, 2 vectors)
def from_motion_to_numpy_vector(motion):
    # For now, we only take the first person. Later we can maybe try to feed in all people, or do batches of two
    motion_vector = np.zeros((250, NUM_BODY_PARTS, 2))
    for i, frame in enumerate(motion):
        if len(frame) > 0 and i < TOTAL_FRAMES:
            current_frame_data = frame
            # TODO extend this past just 1 person
            person0 = current_frame_data[0][1:]
            current_frame_vector = np.zeros((NUM_BODY_PARTS, 2))
            current_body_part_idx = 0
            for body_part_data in person0:
                body_part = body_part_data[0]
                if body_part not in ['left_eye', 'left_ear', 'right_eye', 'right_ear']:
                    current_frame_vector[current_body_part_idx] = body_part_data[1]
                    current_body_part_idx = current_body_part_idx + 1
            motion_vector[i] = current_frame_vector
    return motion_vector

def from_numpy_vector_to_motion_coordinates(motion_vector):
    # Reshape so each element in array is an a NUM_BODY_PARTS x 2 array that has coordinates
    return motion_vector.reshape(TOTAL_FRAMES, NUM_BODY_PARTS, 2)

class LetsDanceDataset(torch.utils.data.Dataset):
    categories_hash = {'tango': 0, 'break': 1, 'swing': 2,'quickstep': 3,
                  'foxtrot': 4,'pasodoble': 5,'tap': 6,'samba': 7,'flamenco': 8,
                  'ballet': 9,'rumba': 10,'waltz': 11,'cha': 12,'latin': 13,
                  'square': 14,'jive': 15}
    
    def __init__(self, root_dir, dances):
        super().__init__()
        self.root_dir = root_dir
        
        self.data = np.zeros((len(dances), TOTAL_FRAMES, NUM_BODY_PARTS, 2))
        self.metadata = dances
        
        dances = list(filter(lambda dance: dance[2] >= TOTAL_FRAMES, dances))
        
        for i, dance in enumerate(tqdm(dances)):
            [category, dance_id, frames] = dance
            current_frame_path = "{}{}/{}.json".format(root_dir, category, dance_id)
            with open(current_frame_path) as f:
                motion = json.load(f)
            self.data[i] = from_motion_to_numpy_vector(motion)
        
        f.close()
        
    def __len__(self):
        return len(self.data)
    
    def getitem_metadata(self, index):
        return self.metadata[index]
    
    def __getitem__(self, index):
        '''
        Returns (category, motion)
        motion is in shape of `(NUM_FRAMES, 26)`
        data is normalized 
        '''
        # todo add transform
        data = torch.Tensor(self.data[index])
        data = normalize(data)
        return data.reshape(250, 26)

    def get_num_body_parts(self):
        # we treat x and y as different
        # TODO - this is kinda janky
        return NUM_BODY_PARTS * 2 
    

# Precomputed
LETS_DANCE_MEAN=torch.Tensor([[722.8463, 230.9753], [725.5026, 284.8430], [718.0136, 283.9306], [729.7226, 332.3776], 
        [717.4737, 331.9450], [731.9489, 333.1949], [719.6969, 335.0007], [724.7956, 446.3675],
        [719.7034, 446.8887], [727.5336, 563.0570], [720.0659, 563.5020], [729.5637, 658.3285],
        [716.7125, 658.4642]])

LETS_DANCE_STD = torch.Tensor([[248.5471,  54.5708], [253.7432,  50.6963], [256.4125,  50.9480], [259.8698,  64.7350],
        [262.0792,  64.8512], [262.9285,  85.9804], [260.5722,  86.1529], [254.4909,  51.1837],
        [256.7613,  51.5563], [253.6787,  62.7815], [256.8294,  62.8685], [260.5059,  70.0873],
        [262.8192,  68.4242]])
        
def normalize(motion):
    return (motion - LETS_DANCE_MEAN) / (LETS_DANCE_STD)

def denormalize(motion):
    return (motion * LETS_DANCE_STD) + LETS_DANCE_MEAN

def save_data(filename, np_array):
    # TODO 
    file_path = 'data/' + filename + ".json"
    d = np_array.tolist()
    d = from_numpy_vector_to_motion_coordinates(np_array).tolist()
    json.dump(d, codecs.open(file_path, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True)

# For this first test, we are just using Latin dances
with open(FRAME_LIST_INDEX) as f:
    frames_index = json.load(f)
    np.random.shuffle(frames_index)

    
train_dances= frames_index[:10]
valid_dances = frames_index[10:20]
train_dataset = LetsDanceDataset('../densepose/full/', train_dances)
valid_dataset = LetsDanceDataset('../densepose/full/', valid_dances)

# mini_dataset = LetsDanceDataset('../densepose/full/', frames_index[:10])
