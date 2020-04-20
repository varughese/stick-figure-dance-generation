import numpy as np
import json, codecs
import os
import torch
import torchvision
import matplotlib.pyplot as plt
import torch.nn as nn
import torch.optim as optim
from torch.autograd.variable import Variable
from torch.utils.data import DataLoader

# We preprocess'd the file names so we have a index with a list of all frames per dance id
FRAME_LIST_INDEX = './dance-frame-list.json'

# np.random.seed(0)
NUM_BODY_PARTS = 13
TOTAL_FRAMES = 250

# We have 250 frames. We are going to going to take the 17 body parts, 
# and turn it into 13 (remove eyes and ears). Then 13x2 (13 body parts, 2 vectors), gets shaped to
# 26. We then take that 26, and convert it into a 250 x 26, each frame shows a body part.
def from_motion_to_numpy_vector(motion):
    # For now, we only take the first person. Later we can maybe try to feed in all people, or do batches of two
    motion_vector = np.zeros((250, NUM_BODY_PARTS * 2))
    if len(motion) < 250:
        print("We need 250 frames.")
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
            motion_vector[i] = current_frame_vector.reshape(NUM_BODY_PARTS * 2)
    # TODO do data normalization
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
        category = 'latin'

        # TODO make this for more than just latin dances
        dances = latin_dances
        
        self.data = np.zeros((len(latin_dances), TOTAL_FRAMES, NUM_BODY_PARTS * 2))
        self.metadata = latin_dances
        
        # for i, dance in enumerate(latin_dances):
        #     [category, dance_id, frames] = dance
        #     current_frame_path = "{}{}/{}.json".format(root_dir, category, dance_id)
        #     with open(current_frame_path) as f:
        #         motion = json.load(f)
        #     self.data[i] = from_motion_to_numpy_vector(motion)
            
        f.close()
        
    def __len__(self):
        return len(self.data)
    
    def getitem_metadata(self, index):
        return self.metadata[index]
    
    def __getitem__(self, index):
        return torch.Tensor(self.data[index])

    def get_num_body_parts(self):
        return NUM_BODY_PARTS * 2 # x + y # FIX

    def save_data(self, filename, np_array):
        # TODO 
        file_path = 'data/' + filename + ".json"
#         np_array = data.cpu().detach().numpy()
        d = from_numpy_vector_to_motion_coordinates(np_array).tolist()
        json.dump(d, codecs.open(file_path, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True)
    


# For this first test, we are just using Latin dances
with open(FRAME_LIST_INDEX) as f:
    frames_index = json.load(f)

latin_dances = list(filter(lambda dance: dance[0] == 'latin' and dance[2] >= TOTAL_FRAMES, frames_index))
train_dataset = LetsDanceDataset('../densepose/full/', latin_dances)
# valid_dataloader = LetsDanceDataset('../densepose/full/', latin_dances[40:])