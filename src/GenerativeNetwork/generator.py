import tensorflow as tf
import numpy as np
import cv2

from tensorflow.keras.callbacks import TensorBoard  # type: ignore
from tensorflow.keras import layers  # type: ignore
from tensorflow.keras.models import Model  # type: ignore
import os
from utils import apply_cfa


class Generator:
    def __init__(self, input_shape, num_classes):
        self.model = None
        self.model_name = None
        self.input_width, self.input_height, self.input_channels = input_shape
        self.num_classes = num_classes

    def __generate_model_name(self):
        model_name = f"Generator"

        return model_name

    # def create_model(self, model_name = None):

    #     shape = (self.input_width, self.input_height, self.input_channels)
    #     gen_input = layers.Input(shape=shape)
    #     # label_input = layers.Input(shape=(self.num_classes, ))
    #     # # Expand the last dimension of label_input from (None, 4) to (None, 4, 1)
    #     # expanded_label_input = layers.Reshape((4,))(label_input)

    #     # # Repeat the expanded_label_input along the new dimension to match the spatial dimensions of the image
    #     # repeated_label_input = layers.RepeatVector(1080*1920)(expanded_label_input)

    #     # # Reshape repeated_label_input to have shape (None, 1080, 1920, 4)
    #     # reshaped_label_input = layers.Reshape((1080, 1920, 4))(repeated_label_input)

    #     # input_layer = layers.Concatenate(axis=-1)([gen_input, reshaped_label_input])
    #     input_layer = gen_input

    #     # block 1
    #     conv2d_1 = layers.Conv2D(64, kernel_size = 3, strides=1, padding='same')(input_layer)
    #     act1 = layers.LeakyReLU()(conv2d_1)

    #     conv2d_2 = layers.Conv2D(64, kernel_size=3, strides=1, padding='same')(act1)
    #     act2 = layers.LeakyReLU()(conv2d_2)

    #     conv2d_3 = layers.Conv2D(32, kernel_size=1, strides=1, padding='same')(act2)
    #     act3 = layers.LeakyReLU()(conv2d_3)

    #     # block 2
    #     conv2d_4 = layers.Conv2D(128, kernel_size = 3, strides=1, padding='same')(act3)
    #     act4 = layers.LeakyReLU()(conv2d_4)

    #     conv2d_5 = layers.Conv2D(128, kernel_size=3, strides=1, padding='same')(act4)
    #     act5 = layers.LeakyReLU()(conv2d_5)

    #     conv2d_6 = layers.Conv2D(128, kernel_size=1, strides=1, padding='same')(act5)
    #     act6 = layers.LeakyReLU()(conv2d_6)

    #     # feature map reduction
    #     conv2d_7 = layers.Conv2D(3, kernel_size=3, strides=1, padding='same')(act6)

    #     generator_output = layers.Activation('tanh')(conv2d_7)
    #     generator_output = layers.Reshape(shape)(generator_output)

    #     # model = Model([gen_input, label_input], generator_output)
    #     model = Model(gen_input, generator_output)

    #     self.model_name = self.__generate_model_name()
    #     self.model = model

    #     return model

    def create_model(self, model_name=None):
        shape = (self.input_width, self.input_height, self.input_channels)
        gen_input = layers.Input(shape=shape)

        # original image size -> downsample -> downsample-> upsample -> upsample -> original image size

        # downsample
        downsample1 = layers.Conv2D(64, (2, 2), strides=2, use_bias=False)(gen_input)
        batch_norm1 = layers.BatchNormalization()(downsample1)
        act1 = layers.LeakyReLU()(batch_norm1)
        # tf.print(act1.shape)

        downsample2 = layers.Conv2D(128, (2, 2), strides=2, use_bias=False)(act1)
        batch_norm2 = layers.BatchNormalization()(downsample2)
        act2 = layers.LeakyReLU()(batch_norm2)
        # tf.print(act2.shape)

        # upsample
        upsample1 = layers.UpSampling2D()(act2)
        upsample1 = layers.Conv2D(64, (2, 2), strides=1, padding="same")(upsample1)
        batch_norm3 = layers.BatchNormalization()(upsample1)
        act3 = layers.LeakyReLU()(batch_norm3)
        # tf.print(act3.shape)

        upsample2 = layers.UpSampling2D()(act3)
        upsample2 = layers.Conv2D(3, (2, 2), strides=1, padding="same")(upsample2)
        batch_norm4 = layers.BatchNormalization()(upsample2)
        act4 = layers.LeakyReLU()(batch_norm4)
        # tf.print(act4.shape)

        # feature map reduction. no batch norm in outlayer
        conv2d = layers.Conv2D(
            self.input_channels, kernel_size=(2, 2), strides=1, padding="same"
        )(act4)
        tf.print(conv2d.shape)

        # output
        generator_output = layers.Activation("tanh")(conv2d)
        generator_output = layers.Reshape(shape)(generator_output)

        model = Model(gen_input, generator_output)

        self.model_name = self.__generate_model_name()
        self.model = model

        return model

    def print_model_summary(self):
        if self.model is None:
            print("Can't print model summary, self.model is None!")
        else:
            print(f"\nSummary of model:\n{self.model.summary()}")
