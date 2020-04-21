# Adapted from github crrngan.pytorch

import os
from argparse import ArgumentParser

import torch
import torch.nn as nn
from torch import optim
import dataloader as dance_dataloader
from c_rnn_gan import Generator, Discriminator
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter

DATA_DIR = 'data'
CKPT_DIR = 'models'

G_FN = 'c_rnn_gan_g.pth'
D_FN = 'c_rnn_gan_d.pth'

G_LRN_RATE = 0.001
D_LRN_RATE = 0.001
MAX_GRAD_NORM = 5.0
# following values are modified at runtime
MAX_SEQ_LEN = 200
BATCH_SIZE = 10

EPSILON = 1e-40 # value to use to approximate zero (to prevent undefined results)

experiment_name = str(torch.rand(1).item())[4:]
print("Experiment Name:", experiment_name)
os.makedirs('trials/'+experiment_name, exist_ok=True)
writer = SummaryWriter(log_dir='trials/' + experiment_name)

class GLoss(nn.Module):
    ''' C-RNN-GAN generator loss
    '''
    def __init__(self):
        super(GLoss, self).__init__()

    def forward(self, logits_gen):
        logits_gen = torch.clamp(logits_gen, EPSILON, 1.0)
        batch_loss = -torch.log(logits_gen)

        return torch.mean(batch_loss)


class DLoss(nn.Module):
    ''' C-RNN-GAN discriminator loss
    '''
    def __init__(self, label_smoothing=False):
        super(DLoss, self).__init__()
        self.label_smoothing = label_smoothing

    def forward(self, logits_real, logits_gen):
        ''' Discriminator loss

        logits_real: logits from D, when input is real
        logits_gen: logits from D, when input is from Generator

        loss = -(ylog(p) + (1-y)log(1-p))

        '''
        logits_real = torch.clamp(logits_real, EPSILON, 1.0)
        d_loss_real = -torch.log(logits_real)

        if self.label_smoothing:
            p_fake = torch.clamp((1 - logits_real), EPSILON, 1.0)
            d_loss_fake = -torch.log(p_fake)
            d_loss_real = 0.9*d_loss_real + 0.1*d_loss_fake

        logits_gen = torch.clamp((1 - logits_gen), EPSILON, 1.0)
        d_loss_gen = -torch.log(logits_gen)

        batch_loss = d_loss_real + d_loss_gen
        return torch.mean(batch_loss)


def run_training(model, optimizer, criterion, dataloader, freeze_g=False, freeze_d=False):
    ''' Run single training epoch
    '''
    
    num_feats = dance_dataloader.NUM_FEATURES
    # dataloader.rewind(part='train')
    # batch_meta, dance = dataloader.get_batch(BATCH_SIZE, MAX_SEQ_LEN, part='train')

    model['g'].train()
    model['d'].train()

    loss = {}
    g_loss_total = 0.0
    d_loss_total = 0.0
    num_corrects = 0
    num_sample = 0

    for step, dance in enumerate(dataloader):

        real_batch_sz = dance.shape[0]

        # get initial states
        # each batch is independent i.e. not a continuation of previous batch
        # so we reset states for each batch
        # POSSIBLE IMPROVEMENT: next batch is continuation of previous batch
        g_states = model['g'].init_hidden(real_batch_sz)
        d_state = model['d'].init_hidden(real_batch_sz)

        #### GENERATOR ####
        if not freeze_g:
            optimizer['g'].zero_grad()
        # prepare inputs
        z = torch.empty([real_batch_sz, MAX_SEQ_LEN, num_feats]).uniform_() # random vector
        dance = torch.Tensor(dance)

        # feed inputs to generator
        g_feats, _ = model['g'](z, g_states)

        # calculate loss, backprop, and update weights of G
        if isinstance(criterion['g'], GLoss):
            d_logits_gen, _, _ = model['d'](g_feats, d_state)
            loss['g'] = criterion['g'](d_logits_gen)
        else: # feature matching
            # feed real and generated input to discriminator
            _, d_feats_real, _ = model['d'](dance, d_state)
            _, d_feats_gen, _ = model['d'](g_feats, d_state)
            loss['g'] = criterion['g'](d_feats_real, d_feats_gen)

        if not freeze_g:
            loss['g'].backward()
            nn.utils.clip_grad_norm_(model['g'].parameters(), max_norm=MAX_GRAD_NORM)
            optimizer['g'].step()

        #### DISCRIMINATOR ####
        if not freeze_d:
            optimizer['d'].zero_grad()
        # feed real and generated input to discriminator
        d_logits_real, _, _ = model['d'](dance, d_state)
        # need to detach from operation history to prevent backpropagating to generator
        d_logits_gen, _, _ = model['d'](g_feats.detach(), d_state)
        # calculate loss, backprop, and update weights of D
        loss['d'] = criterion['d'](d_logits_real, d_logits_gen)
        if not freeze_d:
            loss['d'].backward()
            nn.utils.clip_grad_norm_(model['d'].parameters(), max_norm=MAX_GRAD_NORM)
            optimizer['d'].step()

        g_loss_total += loss['g'].item()
        d_loss_total += loss['d'].item()
        num_corrects += (d_logits_real > 0.5).sum().item() + (d_logits_gen < 0.5).sum().item()
        num_sample += real_batch_sz

        # # fetch next batch
        # batch_meta, dance = dataloader.get_batch(BATCH_SIZE, MAX_SEQ_LEN, part='train')

    g_loss_avg, d_loss_avg = 0.0, 0.0
    d_acc = 0.0
    if num_sample > 0:
        g_loss_avg = g_loss_total / num_sample
        d_loss_avg = d_loss_total / num_sample
        d_acc = 100 * num_corrects / (2 * num_sample) # 2 because (real + generated)

    return model, g_loss_avg, d_loss_avg, d_acc


def run_validation(model, criterion, dataloader):
    ''' Run single validation epoch
    '''
    num_feats = dance_dataloader.NUM_FEATURES

    model['g'].eval()
    model['d'].eval()

    g_loss_total = 0.0
    d_loss_total = 0.0
    num_corrects = 0
    num_sample = 0

    for step, dance in enumerate(dataloader): 

        real_batch_sz = dance.shape[0]

        # initial states
        g_states = model['g'].init_hidden(real_batch_sz)
        d_state = model['d'].init_hidden(real_batch_sz)

        #### GENERATOR ####
        # prepare inputs
        z = torch.empty([real_batch_sz, MAX_SEQ_LEN, num_feats]).uniform_() # random vector
        dance = torch.Tensor(dance)

        # feed inputs to generator
        g_feats, _ = model['g'](z, g_states)
        # feed real and generated input to discriminator
        d_logits_real, d_feats_real, _ = model['d'](dance, d_state)
        d_logits_gen, d_feats_gen, _ = model['d'](g_feats, d_state)
        # calculate loss
        if isinstance(criterion['g'], GLoss):
            g_loss = criterion['g'](d_logits_gen)
        else: # feature matching
            g_loss = criterion['g'](d_feats_real, d_feats_gen)

        d_loss = criterion['d'](d_logits_real, d_logits_gen)

        g_loss_total += g_loss.item()
        d_loss_total += d_loss.item()
        num_corrects += (d_logits_real > 0.5).sum().item() + (d_logits_gen < 0.5).sum().item()
        num_sample += real_batch_sz

    g_loss_avg, d_loss_avg = 0.0, 0.0
    d_acc = 0.0
    if num_sample > 0:
        g_loss_avg = g_loss_total / num_sample
        d_loss_avg = d_loss_total / num_sample
        d_acc = 100 * num_corrects / (2 * num_sample) # 2 because (real + generated)

    return g_loss_avg, d_loss_avg, d_acc


def run_epoch(model, optimizer, criterion, train_dataloader, valid_dataloader, ep, num_ep,
              freeze_g=False, freeze_d=False, pretraining=False):
    ''' Run a single epoch
    '''
    model, trn_g_loss, trn_d_loss, trn_acc = \
        run_training(model, optimizer, criterion, train_dataloader, freeze_g=freeze_g, freeze_d=freeze_d)

    val_g_loss, val_d_loss, val_acc = run_validation(model, criterion, valid_dataloader)

    if pretraining:
        print("Pretraining Epoch %d/%d " % (ep+1, num_ep), "[Freeze G: ", freeze_g, ", Freeze D: ", freeze_d, "]")
    else:
        print("Epoch %d/%d " % (ep+1, num_ep), "[Freeze G: ", freeze_g, ", Freeze D: ", freeze_d, "]")
    print("\t[Training] G_loss: %0.8f, D_loss: %0.8f, D_acc: %0.2f" %  (trn_g_loss, trn_d_loss, trn_acc))
    print("\t[Validation] G_loss: %0.8f, D_loss: %0.8f, D_acc: %0.2f" % (val_g_loss, val_d_loss, val_acc))
    
    writer.add_scalar('G Loss [Training]', trn_g_loss, ep)
    writer.add_scalar('D Loss [Training]', trn_d_loss, ep)
    writer.add_scalar('D Acc [Training]', trn_acc, ep)
    writer.add_scalar('G Loss [Validation]', val_g_loss, ep)
    writer.add_scalar('D Loss [Validation]', val_d_loss, ep)
    writer.add_scalar('D Acc [Validation]', val_acc, ep)

    # -- DEBUG --
    # This is for monitoring the current output from generator
    # generate from model then save as a json file for motion file
    g_states = model['g'].init_hidden(1)
    num_feats = dance_dataloader.NUM_FEATURES
    z = torch.empty([1, MAX_SEQ_LEN, num_feats]).uniform_() # random vector
    if torch.cuda.is_available():
        z = z.cuda()
        model['g'].cuda()

    model['g'].eval()
    g_feats, _ = model['g'](z, g_states)
    dance_data = g_feats.squeeze().cpu()
    dance_data = dance_dataloader.denormalize(dance_data)
    dance_data = dance_data.detach().numpy()


    if (ep+1) == num_ep:
        generated_dance = dance_dataloader.save_data('{}_sample{}_final.dance'.format(experiment_name, ep), dance_data)
    elif ep % 50 == 0:
        generated_dance = dance_dataloader.save_data('{}_sample{}.dance'.format(experiment_name, ep), dance_data)
    # -- DEBUG --

    return model, trn_acc


def main(args):
    ''' Training sequence
    '''
    train_dataset = dance_dataloader.train_dataset
    valid_dataset = dance_dataloader.valid_dataset
    train_loader = DataLoader(train_dataset,
                            batch_size=BATCH_SIZE,
                            hidden_units=1024,
                            shuffle=True)
    valid_loader = DataLoader(valid_dataset,
                            batch_size=BATCH_SIZE,
                            hidden_units=1024,
                            shuffle=True)

    num_feats = dance_dataloader.NUM_FEATURES

    # First checking if GPU is available
    train_on_gpu = torch.cuda.is_available()
    if train_on_gpu:
        print('Training on GPU.')
    else:
        print('No GPU available, training on CPU.')

    model = {
        'g': Generator(num_feats, hidden_units=1024, drop_prob=0.03, use_cuda=train_on_gpu),
        'd': Discriminator(num_feats, hidden_units=1024, drop_prob=0.03, use_cuda=train_on_gpu)
    }

    if args.use_sgd:
        optimizer = {
            'g': optim.SGD(model['g'].parameters(), lr=args.g_lrn_rate, momentum=0.9),
            'd': optim.SGD(model['d'].parameters(), lr=args.d_lrn_rate, momentum=0.9)
        }
    else:
        optimizer = {
            'g': optim.Adam(model['g'].parameters(), args.g_lrn_rate),
            'd': optim.Adam(model['d'].parameters(), args.d_lrn_rate)
        }

    criterion = {
        'g': nn.MSELoss(reduction='sum') if args.feature_matching else GLoss(),
        'd': DLoss(args.label_smoothing)
    }

    if args.load_g:
        ckpt = torch.load(os.path.join(CKPT_DIR, G_FN))
        model['g'].load_state_dict(ckpt)
        print("Continue training of %s" % os.path.join(CKPT_DIR, G_FN))

    if args.load_d:
        ckpt = torch.load(os.path.join(CKPT_DIR, D_FN))
        model['d'].load_state_dict(ckpt)
        print("Continue training of %s" % os.path.join(CKPT_DIR, D_FN))

    if train_on_gpu:
        model['g'].cuda()
        model['d'].cuda()

    if not args.no_pretraining:
        for ep in range(args.d_pretraining_epochs):
            model, _ = run_epoch(model, optimizer, criterion, train_loader,valid_loader,
                              ep, args.d_pretraining_epochs, freeze_g=True, pretraining=True)

        for ep in range(args.g_pretraining_epochs):
            model, _ = run_epoch(model, optimizer, criterion, train_loader, valid_loader,
                              ep, args.g_pretraining_epochs, freeze_d=True, pretraining=True)

    freeze_d = False
    for ep in range(args.num_epochs):
        # if ep % args.freeze_d_every == 0:
        #     freeze_d = not freeze_d

        model, trn_acc = run_epoch(model, optimizer, criterion, train_loader, valid_loader, ep, args.num_epochs, freeze_d=freeze_d)
        if args.conditional_freezing:
            # conditional freezing
            freeze_d = False
            if trn_acc >= 95.0:
                freeze_d = True

    if not args.no_save_g:
        torch.save(model['g'].state_dict(), os.path.join(CKPT_DIR, G_FN))
        print("Saved generator: %s" % os.path.join(CKPT_DIR, G_FN))

    if not args.no_save_d:
        torch.save(model['d'].state_dict(), os.path.join(CKPT_DIR, D_FN))
        print("Saved discriminator: %s" % os.path.join(CKPT_DIR, D_FN))


# if __name__ == "__main__":

# ARG_PARSER = ArgumentParser()
# ARG_PARSER.add_argument('--load_g', action='store_true')
# ARG_PARSER.add_argument('--load_d', action='store_true')
# ARG_PARSER.add_argument('--no_save_g', action='store_true')
# ARG_PARSER.add_argument('--no_save_d', action='store_true')

# ARG_PARSER.add_argument('--num_epochs', default=300, type=int)
# ARG_PARSER.add_argument('--batch_size', default=16, type=int)
# ARG_PARSER.add_argument('--g_lrn_rate', default=0.001, type=float)
# ARG_PARSER.add_argument('--d_lrn_rate', default=0.001, type=float)

# ARG_PARSER.add_argument('--no_pretraining', action='store_true')
# ARG_PARSER.add_argument('--g_pretraining_epochs', default=5, type=int)
# ARG_PARSER.add_argument('--d_pretraining_epochs', default=5, type=int)
# ARG_PARSER.add_argument('--use_sgd', action='store_true')
# ARG_PARSER.add_argument('--conditional_freezing', action='store_true')
# ARG_PARSER.add_argument('--label_smoothing', action='store_true')
# ARG_PARSER.add_argument('--feature_matching', action='store_true')

class ARGS():
    def __init__(self):
        self.load_g =  False
        self.load_d =  False
        self.no_save_g =  False
        self.no_save_d =  False

        self.num_epochs =  1000
        self.batch_size =  8
        self.g_lrn_rate =  0.008
        self.d_lrn_rate =  0.008

        self.no_pretraining =  False
        self.g_pretraining_epochs =  5
        self.d_pretraining_epochs =  5
        self.use_sgd =  False
        self.conditional_freezing =  True
        self.label_smoothing =  False
        self.feature_matching =  True
ARGS = ARGS()
# ARGS = ARG_PARSER.parse_args()
MAX_SEQ_LEN = 250 # todo make this better
BATCH_SIZE = ARGS.batch_size

main(ARGS)
