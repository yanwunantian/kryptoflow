#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import pytest
from sklearn.datasets import make_classification
from keras.engine.training import Model as KerasBaseModel
from keras import backend as K
from keras.models import Sequential
from keras.utils.test_utils import keras_test
from keras.layers import Dense, Activation
from kryptoflow.models.model import KerasModel, TrainableModel
import shutil
from kryptoflow.definitions import SAVED_MODELS


__author__ = "Carlo Mazzaferro"
__copyright__ = "Carlo Mazzaferro"
__license__ = "GNU GPL v2"


# @pytest.fixture
# def cleanup():
#     for root, dirs, files in os.walk(SAVED_MODELS):
#         for f in files:
#             os.unlink(os.path.join(root, f))
#         for d in dirs:
#             shutil.rmtree(os.path.join(root, d))


@pytest.fixture(scope='function')
def keras_model():
    x, y = make_classification(n_features=2, n_redundant=0, n_informative=1, n_clusters_per_class=1)
    model = Sequential()
    model.add(Dense(64, input_dim=2, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy',
                  optimizer='rmsprop',
                  metrics=['accuracy'])
    model.fit(x, y)
    return model


@pytest.fixture
def serializer():
    skl = KerasModel(artifact=keras_model)
    skl.store(name='nn')


@keras_test
def test_serialization(keras_model):
    skl = KerasModel(artifact=keras_model)
    skl.store(name='nn')
    assert os.path.exists(os.path.join(skl.model_path, 'nn' + '.h5'))
    assert os.path.exists(os.path.join(skl.model_path, 'nn' + '.json'))
    assert os.path.exists(os.path.join(skl.model_path, 'tf', 'saved_model' + '.pb'))
    assert os.path.isdir(os.path.join(skl.model_path, 'tf', 'variables'))

    for root, dirs, files in os.walk(SAVED_MODELS):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


@keras_test
def test_mulitple_serializations_first(keras_model):
    skl1 = KerasModel(artifact=keras_model)
    skl1.store(name='nn1')
    assert os.path.exists(skl1.model_path)


@keras_test
def test_mulitple_serializations_second(keras_model):
    skl2 = KerasModel(artifact=keras_model)
    skl2.store(name='nn2')
    assert os.path.exists(skl2.model_path)


@keras_test
def test_mulitple_serializations_third(keras_model):
    skl3 = KerasModel(artifact=keras_model)
    skl3.store(name='nn3')
    assert len(os.listdir(SAVED_MODELS)) == 3

    # cleanup
    for root, dirs, files in os.walk(SAVED_MODELS):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


@keras_test
def test_loader(keras_model):
    skl = KerasModel(artifact=keras_model)
    skl.store(name='nn')
    K.clear_session()
    reloaded = skl.load(name='nn')
    assert isinstance(reloaded, KerasBaseModel)

    for root, dirs, files in os.walk(SAVED_MODELS):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


@keras_test
def test_trainable_model_from_file(keras_model):
    skl = KerasModel(artifact=keras_model)
    skl.store(name='nn')

    K.clear_session()
    trainable = TrainableModel.from_file(run_number=1, name='nn', model_type='keras')
    assert isinstance(trainable.model, KerasBaseModel)
    for root, dirs, files in os.walk(SAVED_MODELS):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


@keras_test
def test_trainable_model(keras_model):
    trainable = TrainableModel(keras_model)
    assert isinstance(trainable.model, KerasBaseModel)
    assert isinstance(trainable.serializer, KerasModel)
    for root, dirs, files in os.walk(SAVED_MODELS):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))