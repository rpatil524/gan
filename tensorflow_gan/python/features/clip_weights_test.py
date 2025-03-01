# coding=utf-8
# Copyright 2024 The TensorFlow GAN Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for tfgan.features.clip_weights."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

import tensorflow as tf
import tensorflow_gan as tfgan


class ClipWeightsTest(tf.test.TestCase):
  """Tests for `discriminator_weight_clip`."""

  def setUp(self):
    super(ClipWeightsTest, self).setUp()
    self.variables = [tf.Variable(2.0)]
    self.tuple = collections.namedtuple('VarTuple',
                                        ['discriminator_variables'])(
                                            self.variables)

  def _test_weight_clipping_helper(self, use_tuple):
    loss = self.variables[0]
    opt = tf.compat.v1.train.GradientDescentOptimizer(1.0)
    if use_tuple:
      opt_clip = tfgan.features.clip_variables(opt, self.variables, 0.1)
    else:
      opt_clip = tfgan.features.clip_discriminator_weights(opt, self.tuple, 0.1)

    train_op1 = opt.minimize(loss, var_list=self.variables)
    train_op2 = opt_clip.minimize(loss, var_list=self.variables)

    with self.cached_session(use_gpu=True) as sess:
      sess.run(tf.compat.v1.global_variables_initializer())
      self.assertEqual(2.0, sess.run(self.variables[0]))
      sess.run(train_op1)
      self.assertLess(0.1, sess.run(self.variables[0]))

    with self.cached_session(use_gpu=True) as sess:
      sess.run(tf.compat.v1.global_variables_initializer())
      self.assertEqual(2.0, sess.run(self.variables[0]))
      sess.run(train_op2)
      self.assertNear(0.1, sess.run(self.variables[0]), 1e-7)

  def test_weight_clipping_argsonly(self):
    if tf.executing_eagerly():
      # Optimizers work differently in eager.
      return
    self._test_weight_clipping_helper(False)

  def test_weight_clipping_ganmodel(self):
    if tf.executing_eagerly():
      # Optimizers work differently in eager.
      return
    self._test_weight_clipping_helper(True)

  def _test_incorrect_weight_clip_value_helper(self, use_tuple):
    opt = tf.compat.v1.train.GradientDescentOptimizer(1.0)

    if use_tuple:
      with self.assertRaisesRegex(ValueError, 'must be positive'):
        tfgan.features.clip_discriminator_weights(
            opt, self.tuple, weight_clip=-1)
    else:
      with self.assertRaisesRegex(ValueError, 'must be positive'):
        tfgan.features.clip_variables(opt, self.variables, weight_clip=-1)

  def test_incorrect_weight_clip_value_argsonly(self):
    self._test_incorrect_weight_clip_value_helper(False)

  def test_incorrect_weight_clip_value_tuple(self):
    self._test_incorrect_weight_clip_value_helper(True)


if __name__ == '__main__':
  tf.test.main()
