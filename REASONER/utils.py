# -*- coding: utf-8 -*-
# @Time   : 2023/02/06
# @Author : Jingsen Zhang
# @Email  : zhangjingsen@ruc.edu.cn

import torch
import random
import datetime
import numpy as np
import importlib

from data.dataloader import TagDataLoader, ReviewDataLoader


def get_model(model_name):
    r"""Automatically select model class based on model name

    Args:
        model_name (str): model name

    Returns:
        Recommender: model class
    """
    model_submodule = ['tag_aware_recommender', 'review_aware_recommender']
    model_file_name = model_name.lower()
    model_module = None
    for submodule in model_submodule:
        module_path = '.'.join(['model', submodule, model_file_name])
        if importlib.util.find_spec(module_path, __name__):
            model_module = importlib.import_module(module_path, __name__)
            break

    if model_module is None:
        raise ValueError('`model_name` [{}] is not the name of an existing model.'.format(model_name))
    model_class = getattr(model_module, model_name)
    return model_class


def get_trainer(model_type, model_name):
    r"""Automatically select trainer class based on model type and model name

    Args:
        model_type (ModelType): model type
        model_name (str): model name
    Returns:
        Trainer: trainer class
    """
    try:
        return getattr(importlib.import_module('trainer'), model_name + 'Trainer')
    except AttributeError:
        if model_type == 'review_aware':
            return getattr(importlib.import_module('trainer'), 'ReviewTrainer')
        else:
            return getattr(importlib.import_module('trainer'), 'Trainer')


def get_dataloader(model_type):
    """Return a dataloader class.

    """

    if model_type == 'tag_aware':
        return TagDataLoader
    else:
        return ReviewDataLoader


def get_batchify(model_type, model_name, train_type, procedure):
    try:
        return getattr(importlib.import_module('data'), model_name + 'Batchify')
    except AttributeError:
        if model_type == 'review_aware':
            return getattr(importlib.import_module('data'), 'ReviewBatchify')
        else:
            if procedure == 'test':
                return getattr(importlib.import_module('data'), 'TagTestBatchify')
            else:
                if train_type == 'bpr':
                    return getattr(importlib.import_module('data'), 'NegSamplingBatchify')
                else:
                    return getattr(importlib.import_module('data'), 'Batchify')
                
                
def now_time():
    return '[' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ']: '


def get_local_time():
    r"""Get current time

    Returns:
        str: current time
    """
    cur = datetime.datetime.now()
    cur = cur.strftime('%b-%d-%Y_%H-%M-%S')
    return cur


def set_seed(seed):
    r"""
    set seed for random sampling.

    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


def ids2tokens(ids, word2idx, idx2word):  # tranform ids to token_seq(sentence)
    eos = word2idx['<eos>']
    tokens = []
    for i in ids:
        if i == eos:
            break
        tokens.append(idx2word[i])
    return tokens

def two_seq_same(sa, sb):
    if len(sa) != len(sb):
        return False
    for (wa, wb) in zip(sa, sb):
        if wa != wb:
            return False
    return True
    
def unique_sentence_percent(sequence_batch):
    unique_seq = []
    for seq in sequence_batch:
        count = 0
        for uni_seq in unique_seq:
            if two_seq_same(seq, uni_seq):
                count += 1
                break
        if count == 0:
            unique_seq.append(seq)

    return len(unique_seq) / len(sequence_batch), len(unique_seq)


def feature_detect(seq_batch, feature_set):
    feature_batch = []
    for ids in seq_batch:
        feature_list = []
        for i in ids:
            if i in feature_set:
                feature_list.append(i)
        feature_batch.append(set(feature_list))

    return feature_batch


def feature_matching_ratio(feature_batch, test_feature):
    count = 0
    denominador = len(feature_batch)
    for (fea_set, fea) in zip(feature_batch, test_feature):
        if fea == []:
          denominador -= 1
          continue
        try:
          for i in fea:
            if i in fea_set:
                count += 1
        except:
          denominador -= 1

    return count / denominador


def feature_coverage_ratio(feature_batch, feature_set):
    features = set()
    for fb in feature_batch:
        features = features | fb

    return len(features) / len(feature_set)


def feature_diversity(feature_batch):
    list_len = len(feature_batch)

    total_count = 0
    for i, x in enumerate(feature_batch):
        for j in range(i + 1, list_len):
            y = feature_batch[j]
            total_count += len(x & y)

    denominator = list_len * (list_len - 1) / 2
    return total_count / denominator
