# Copyright 2018-2020 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Tests for the templates utility functions.
"""
# pylint: disable=protected-access,cell-var-from-loop
import pytest
import numpy as np
from pennylane.templates.utils import (check_wires,
                                       check_shape,
                                       check_shapes,
                                       get_shape,
                                       check_number_of_layers,
                                       check_is_in_options,
                                       check_type)

#########################################
# Inputs

WIRES_PASS = [(0, [0]),
              ([4], [4]),
              ([1, 2], [1, 2])]
WIRES_FAIL = [[-1],
              ['a'],
              lambda x: x,
              None
              ]

SHAPE_PASS = [(0.231, (), None),
              ([[1., 2.], [3., 4.]], (2, 2), None),
              ([-2.3], (1,), None),
              ([-2.3, 3.4], (4,), 'max'),
              ([-2.3, 3.4], (1,), 'min'),
              ([-2.3], (1,), 'max'),
              ([-2.3], (1,), 'min'),
              ([[-2.3, 3.4], [1., 0.2]], (3, 3), 'max'),
              ([[-2.3, 3.4, 1.], [1., 0.2, 1.]], (1, 2), 'min'),
              ]

SHAPE_LST_PASS = [([0.231, 0.1], [(), ()], None),
                  ([[1., 2.], [4.]], [(2,), (1,)], None),
                  ([[-2.3], -1.], [(1,), ()], None),
                  ([[-2.3, 0.1], -1.], [(1,), ()], 'min'),
                  ([[-2.3, 0.1], -1.], [(3,), ()], 'max')
                  ]

SHAPE_FAIL = [(0.231, (1,), None),
              ([[1., 2.], [3., 4.]], (2,), None),
              ([-2.3], (4, 5), None),
              ([-2.3, 3.4], (4,), 'min'),
              ([-2.3, 3.4], (1,), 'max'),
              ([[-2.3, 3.4], [1., 0.2]], (3, 3), 'min'),
              ([[-2.3, 3.4, 1.], [1., 0.2, 1.]], (1, 2), 'max'),
              ]

GET_SHAPE_PASS = [(0.231, ()),
                  (complex(1, 0), ()),
                  (1, ()),
                  ([[1., 2.], [3., 4.]], (2, 2)),
                  ([-2.3], (1,)),
                  ([-2.3, 3.4], (2,)),
                  ([-2.3], (1,)),
                  ([[-2.3, 3.4, 1.], [1., 0.2, 1.]], (2, 3)),
                  ]

GET_SHAPE_FAIL = [("a",),
                  (None,)]

SHAPE_LST_FAIL = [([[0.231, 0.1]], [[()], [(3, 4)]], None),
                  ([[1., 2.], [4.]], [(1,), (1,)], None),
                  ([[-2.3], -1.], [(1, 2), (1,)], None),
                  ([[-2.3, 0.1], -1.], [(1,), ()], 'max'),
                  ([[-2.3, 0.1], -1.], [(3,), ()], 'min')
                  ]

LAYERS_PASS = [([[1], [2], [3]], 1),
               ([[[1], [2], [3]], [[1], [2], [3]]], 3),
               ]

LAYERS_FAIL = [([[[1], [2], [3]], 1], 5),
               ([[[1], [2], [3]], [[1], [2]]], 4),
               ]

OPTIONS_PASS = [("a", ["a", "b"])]

OPTIONS_FAIL = [("c", ["a", "b"])]

TYPE_PASS = [(["a"], list, type(None)),
             (1, int, type(None)),
             ("a", int, str),
             ]

TYPE_FAIL = [("a", list, type(None)),
             (type(None), int, list),
             ]


##############################


class TestInputChecks:
    """Test private functions that check the input of templates."""

    @pytest.mark.parametrize("wires, target", WIRES_PASS)
    def test_check_wires(self, wires, target):
        """Tests that wires check returns correct wires list and its length."""
        res = check_wires(wires=wires)
        assert res == target

    @pytest.mark.parametrize("wires", WIRES_FAIL)
    def test_check_wires_exception(self, wires):
        """Tests that wires check fails if ``wires`` is not a positive integer or iterable of positive integers."""
        with pytest.raises(ValueError, match="wires must be a positive integer"):
            check_wires(wires=wires)

    @pytest.mark.parametrize("inpt, target_shape", GET_SHAPE_PASS)
    def test_get_shape(self, inpt, target_shape):
        """Tests that ``get_shape`` returns correct shape."""
        shape = get_shape(inpt)
        assert shape == target_shape

    @pytest.mark.parametrize("inpt", GET_SHAPE_FAIL)
    def test_get_shape_exception(self, inpt):
        """Tests that ``get_shape`` fails if unkown type of arguments."""
        with pytest.raises(ValueError, match="could not extract shape of object"):
            get_shape(inpt)

    @pytest.mark.parametrize("inpt, target_shape, bound", SHAPE_PASS)
    def test_check_shape(self, inpt, target_shape, bound):
        """Tests that shape check succeeds for valid arguments."""
        check_shape(inpt, target_shape, bound=bound, msg="XXX")

    @pytest.mark.parametrize("inpt, target_shape, bound", SHAPE_LST_PASS)
    def test_check_shape_list_of_inputs(self, inpt, target_shape, bound):
        """Tests that list version of shape check succeeds for valid arguments."""
        check_shapes(inpt, target_shape, bounds=[bound] * len(inpt), msg="XXX")

    @pytest.mark.parametrize("inpt, target_shape, bound", SHAPE_FAIL)
    def test_check_shape_exception(self, inpt, target_shape, bound):
        """Tests that shape check fails for invalid arguments."""
        with pytest.raises(ValueError, match="XXX"):
            check_shape(inpt, target_shape, bound=bound, msg="XXX")

    @pytest.mark.parametrize("inpt, target_shape, bound", SHAPE_LST_FAIL)
    def test_check_shape_list_of_inputs_exception(self, inpt, target_shape, bound):
        """Tests that list version of shape check succeeds for valid arguments."""
        with pytest.raises(ValueError, match="XXX"):
            check_shapes(inpt, target_shape, bounds=[bound] * len(inpt), msg="XXX")

    @pytest.mark.parametrize("hp, opts", OPTIONS_PASS)
    def test_check_options(self, hp, opts):
        """Tests that option check succeeds for valid arguments."""
        check_is_in_options(hp, opts, msg="XXX")

    @pytest.mark.parametrize("hp, opts", OPTIONS_FAIL)
    def test_check_options_exception(self, hp, opts):
        """Tests that option check throws error for invalid arguments."""
        with pytest.raises(ValueError, match="XXX"):
            check_is_in_options(hp, opts, msg="XXX")

    @pytest.mark.parametrize("hp, typ, alt", TYPE_PASS)
    def test_check_type(self, hp, typ, alt):
        """Tests that type check succeeds for valid arguments."""
        check_type(hp, [typ, alt], msg="XXX")

    @pytest.mark.parametrize("hp, typ, alt", TYPE_FAIL)
    def test_check_type_exception(self, hp, typ, alt):
        """Tests that type check throws error for invalid arguments."""
        with pytest.raises(ValueError, match="XXX"):
            check_type(hp, [typ, alt], msg="XXX")

    @pytest.mark.parametrize("inpt, repeat", LAYERS_PASS)
    def test_check_num_layers(self, inpt, repeat):
        """Tests that layer check returns correct number of layers."""
        n_layers = check_number_of_layers(inpt)
        assert n_layers == repeat

    @pytest.mark.parametrize("inpt, repeat", LAYERS_FAIL)
    def test_check_num_layers_exception(self, inpt, repeat):
        """Tests that layer check throws exception if number of layers not consistent."""
        with pytest.raises(ValueError, match="The first dimension of all parameters"):
            check_number_of_layers(inpt)
