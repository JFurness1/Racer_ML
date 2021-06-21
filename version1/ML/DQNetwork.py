import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import HyperParameters

class DQNetwork(nn.Module):
    """

    Network:
    [fixed]   |  conv1  | elu | max_pool2d | conv2 | elu | max_pool2d \ Flatten | fc1 | fc2 | out
    [position (x, y), velocity (x, y), direction ] -----------------------^
    """
    def __init__(self, WIDTH, HEIGHT, possible_actions):
        """
        QUEUE_SIZE is "one hot" array for queue of upcoming tetraminos
        """

        super(DQNetwork, self).__init__()
        print("INIT")

        self.CN1_params = {
            'channels_in':2,
            'channels_out':128,
            'kernel':3,
            'stride':1,
            'padding':(1,1),
            'dilation':1,
            'input_width':WIDTH,
            'input_height':HEIGHT,
            'output_width': None,
            'output_height': None
        }
        self.set_output_dims(self.CN1_params)

        self.CN2_params = {
            'channels_in':self.CN1_params['channels_out'],
            'channels_out':64,
            'kernel':3,
            'stride':3,
            'padding':(1,1),
            'dilation':1,
            'input_width':int(self.CN1_params['output_width']/2), # Maxpool
            'input_height':int(self.CN1_params['output_height']/2),
            'output_width': None,
            'output_height': None
        }
        self.set_output_dims(self.CN2_params)

        # input is 25x10x2
        self.conv1 = nn.Conv2d(self.CN1_params['channels_in'], self.CN1_params['channels_out'],
            self.CN1_params['kernel'], stride=self.CN1_params['stride'], padding=self.CN1_params['padding'])
        # elu -> max_pool2d(2, 2)
        
        self.conv2 = nn.Conv2d(self.CN1_params['channels_out'], self.CN2_params['channels_out'],
            self.CN2_params['kernel'], stride=self.CN2_params['stride'], padding=self.CN2_params['padding'])
        # elu -> max_pool2d(2, 2)

        self.conv_net_output =  int(self.CN2_params['channels_out']*self.CN2_params['output_width']*self.CN2_params['output_height']//4 ) # Max pool

        # 5 additional scalar inputs from 
        fc1_dim = 5 + self.conv_net_output
        print("Fully connected input dimensions:", fc1_dim)
        self.fc1 = nn.Linear(fc1_dim, 128) # FIX INPUTS
        self.fc2 = nn.Linear(128, possible_actions)
        # -> Q(s, a)

        self.loss = nn.MSELoss

    def forward(self, inp):
        track = inp[0]  # (height, width)
        scalars = inp[2]  # (queue)

        conv_in = torch.from_numpy(track).unsqueeze(0)
        print(conv_in.shape)
        flat_in = torch.from_numpy(scalars)
        out = self.conv1(conv_in)
        out = F.elu(out)
        out = F.max_pool2d(out, 2, 2)
        out = self.conv2(out)
        out = F.elu(out)
        out = F.max_pool2d(out, 2, 2)
        out = torch.flatten(out)
        print(out.shape, flat_in.shape)
        fc_inp = torch.cat([out, flat_in])
        out = F.elu(self.fc1(fc_inp))
        out = F.elu(self.fc2(out))
        return out

    @staticmethod
    def set_output_dims(params):
        """
        Utility function for computing output of convolutions
        takes a tuple of (h,w) and returns a tuple of (h,w)
        """
        
        h_w = (params['input_height'], params['input_width'])
        
        if type(params['kernel']) is not tuple:
            kernel_size = (params['kernel'], params['kernel'])
        else:
            kernel_size = params['kernel']
        
        if type(params['stride']) is not tuple:
            stride = (params['stride'], params['stride'])
        else:
            stride = params['stride']
        
        if type(params['padding']) is not tuple:
            pad = (params['padding'], params['padding'])
        else:
            pad = params['padding']

        dilation = params['dilation']
        
        params['output_height'] = int((h_w[0] + (2*pad[0]) - (dilation*(kernel_size[0] - 1)) - 1)//stride[0] + 1)
        params['output_width'] = int((h_w[1] + (2*pad[1]) - (dilation*(kernel_size[1] - 1)) - 1)//stride[1] + 1)
