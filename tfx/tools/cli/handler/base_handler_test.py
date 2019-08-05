# Copyright 2019 Google LLC. All Rights Reserved.
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
"""Tests for tfx.tools.cli.handler.base_handler."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import os
import mock

import tensorflow as tf

from tfx.tools.cli import labels
from tfx.tools.cli.handler import base_handler


class FakeHandler(base_handler.BaseHandler):

  def create_pipeline(self) -> None:
    pass

  def update_pipeline(self) -> None:
    pass

  def list_pipelines(self) -> None:
    pass

  def delete_pipeline(self) -> None:
    pass

  def compile_pipeline(self) -> None:
    pass

  def create_run(self) -> None:
    pass

  def delete_run(self) -> None:
    pass

  def terminate_run(self) -> None:
    pass

  def list_runs(self) -> None:
    pass

  def get_run(self) -> None:
    pass


def _MockSubprocess(cmd, env):  # pylint: disable=invalid-name, unused-argument
  # Store pipeline_args in a pickle file
  pipeline_args_path = env[labels.TFX_JSON_EXPORT_PIPELINE_ARGS_PATH]
  pipeline_args = {'pipeline_name': 'pipeline_test_name'}
  with open(pipeline_args_path, 'w') as f:
    json.dump(pipeline_args, f)


class BaseHandlerTest(tf.test.TestCase):

  def setUp(self):
    super(BaseHandlerTest, self).setUp()
    self.engine = 'airflow'
    self.chicago_taxi_pipeline_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'testdata')
    self.pipeline_path = os.path.join(self.chicago_taxi_pipeline_dir,
                                      'test_pipeline_airflow_1.py')

  def test_check_pipeline_dsl_path_invalid(self):
    flags_dict = {labels.ENGINE_FLAG: self.engine,
                  labels.PIPELINE_DSL_PATH: 'taxi_pipeline.py'}
    handler = FakeHandler(flags_dict)
    with self.assertRaises(SystemExit) as err:
      handler._check_pipeline_dsl_path()
    self.assertEqual(str(err.exception), 'Invalid pipeline path: {}'
                     .format(flags_dict[labels.PIPELINE_DSL_PATH]))

  def test_check_dsl_runner_wrong_engine(self):
    flags_dict = {labels.ENGINE_FLAG: 'kubeflow',
                  labels.PIPELINE_DSL_PATH: self.pipeline_path}
    handler = FakeHandler(flags_dict)
    with self.assertRaises(SystemExit) as err:
      handler._check_dsl_runner()
    self.assertEqual(str(err.exception),
                     '{} runner not found in dsl.'
                     .format(flags_dict[labels.ENGINE_FLAG]))

  @mock.patch('subprocess.check_output', _MockSubprocess)
  def test_extract_pipeline_args(self):
    flags_dict = {
        labels.ENGINE_FLAG: 'engine',
        labels.PIPELINE_DSL_PATH: 'path_to_pipeline_dsl'
    }
    handler = FakeHandler(flags_dict)
    pipeline_args = handler._extract_pipeline_args()
    self.assertEqual(pipeline_args, {'pipeline_name': 'pipeline_test_name'})

  def test_get_handler_home(self):
    flags_dict = {
        labels.ENGINE_FLAG: 'engine',
        labels.PIPELINE_DSL_PATH: 'path_to_pipeline_dsl'
    }
    handler = FakeHandler(flags_dict)
    self.assertEqual(
        os.path.join(os.environ['HOME'], 'home_dir', ''),
        handler._get_handler_home('home_dir'))

  def test_check_dsl_runner_airflow(self):
    pipeline_path = os.path.join(self.chicago_taxi_pipeline_dir,
                                 'test_pipeline_airflow_1.py')
    flags_dict = {
        labels.ENGINE_FLAG: 'airflow',
        labels.PIPELINE_DSL_PATH: pipeline_path
    }
    handler = FakeHandler(flags_dict)
    self.assertIsNone(handler._check_dsl_runner())

  def test_check_dsl_runner_kubeflow(self):
    pipeline_path = os.path.join(self.chicago_taxi_pipeline_dir,
                                 'test_pipeline_kubeflow_1.py')
    flags_dict = {
        labels.ENGINE_FLAG: 'kubeflow',
        labels.PIPELINE_DSL_PATH: pipeline_path
    }
    handler = FakeHandler(flags_dict)
    self.assertIsNone(handler._check_dsl_runner())

  def test_check_dsl_runner_beam(self):
    pipeline_path = os.path.join(self.chicago_taxi_pipeline_dir,
                                 'test_pipeline_beam_1.py')
    flags_dict = {
        labels.ENGINE_FLAG: 'beam',
        labels.PIPELINE_DSL_PATH: pipeline_path
    }
    handler = FakeHandler(flags_dict)
    self.assertIsNone(handler._check_dsl_runner())


if __name__ == '__main__':
  tf.test.main()
