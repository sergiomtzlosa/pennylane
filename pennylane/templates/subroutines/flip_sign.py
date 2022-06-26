# Copyright 2018-2021 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
r"""
Contains the FlipSign template.
"""

import numpy as np
import pennylane as qml
from pennylane.operation import Operation, AnyWires


class FlipSign(Operation):
    r"""FlipSign operator flips the sign for a given basic state.

    In a nutshell, this class perform the following operation:

    FlipSign(n):math:`|m\rangle = -|m\rangle` if m = n
    FlipSign(n):math:`|m\rangle = |m\rangle` if m != n

    Where n is the basic state to flip and m is the input.
    It flips the sign of the state.

    Args:
        n (array[int] or int): binary array or integer value representing the state to flip the sign
        wires (array[int]): number of wires that the operator acts on

    Raises:
        ValueError: "expected at integer array for wires "
        ValueError: "expected at least one wire representing the qubit "
        ValueError: "expected at integer equal or greater than zero for basic flipping state "
        ValueError: "expected at integer binary array "

    .. seealso:: :func:`~.relevant_func`, :class:`~.RelevantClass` (optional)

    .. details::

        :title: Usage Details

        The template is used inside a qnode.
        The number of shots has to be explicitly set on the device when using sample-based measurements:

        .. code-block:: python

            dev = qml.device("default.qubit", wires=2, shots = 1)

            @qml.qnode(dev)
            def circuit():
               for wire in list(range(2)):
                    qml.Hadamard(wires = wire)
               qml.FlipSign([1,0], wires = list(range(2)))
               return qml.sample()

            circuit()

        The result for the above circuit is:

            >>> print(drawer())
            0: ──H─╭FlipSign──H─┤  Sample
            1: ──H─├FlipSign──H─┤  Sample
            2: ──H─├FlipSign──H─┤  Sample
            3: ──H─├FlipSign──H─┤  Sample
            4: ──H─╰FlipSign──H─┤  Sample

    """

    num_wires = AnyWires

    def __init__(self, n, wires, do_queue=True, id=None):

        if not isinstance(wires, list):
            raise ValueError("expected at integer array for wires ")

        if len(wires) == 0:
            raise ValueError("expected at least one wire representing the qubit ")

        if np.array(wires).dtype != np.dtype("int"):
            raise ValueError("expected at integer binary array ")

        if (
            isinstance(n, list)
            and np.array(wires).dtype != np.dtype("int")
            and self.is_binary_array(n)
        ):
            n = self.to_number(n)

        if type(n) == int:
            if n >= 0:
                n = self.to_list(n, len(wires))
            else:
                raise ValueError(
                    "expected at integer equal or greater than zero for basic flipping state "
                )
        else:
            raise ValueError(
                "expected at integer equal or greater than zero for basic flipping state "
            )

        if np.array(n).dtype != np.dtype("int"):
            raise ValueError("expected at integer binary array ")

        self._hyperparameters = {"n": n}
        super().__init__(wires=wires, do_queue=do_queue, id=id)

    @staticmethod
    def is_binary_array(arr):
        r"""Check if array is binary or not (only 0's and 1's)

        Returns:
            (bool): boolean that checks whether array is binary or not
        """
        return np.array_equal(arr, arr.astype(bool))

    @staticmethod
    def to_list(n, n_wires):
        r"""Convert an integer into a binary integer list

        Raises:
            ValueError: "cannot encode n with n wires "

        Returns:
            (array[int]): integer binary array
        """
        if n >= 2**n_wires:
            raise ValueError("cannot encode n with n wires ")

        b_str = f"{n:b}".zfill(n_wires)
        bin_list = [int(i) for i in b_str]
        return bin_list

    @staticmethod
    def to_number(arr_bin):
        r"""Convert a binary array to integer number

        Returns:
            (int): integer number
        """
        return sum([arr_bin[i] * 2 ** (len(arr_bin) - i - 1) for i in range(len(arr_bin))])

    @property
    def num_params(self):
        return 0

    @staticmethod
    def compute_decomposition(wires, n):  # pylint: disable=arguments-differ
        r"""Representation of the operator

        .. seealso:: :meth:`~.FlipSign.decomposition`.

        Args:
            wires (array[int]): wires that the operator acts on
            n (array[int]): binary array vector representing the state to flip the sign

        Raises:
            ValueError: "Wires length and flipping state length does not match, they must be equal length "

        Returns:
            list[Operator]: decomposition of the operator
        """

        op_list = []

        if len(wires) == len(n):
            if n[-1] == 0:
                op_list.append(qml.PauliX(wires[-1]))

            op_list.append(
                qml.ctrl(qml.PauliZ, control=wires[:-1], control_values=n[:-1])(wires=wires[-1])
            )

            if n[-1] == 0:
                op_list.append(qml.PauliX(wires[-1]))
        else:
            raise ValueError(
                "Wires length and flipping state length does not match, they must be equal length "
            )

        return op_list
