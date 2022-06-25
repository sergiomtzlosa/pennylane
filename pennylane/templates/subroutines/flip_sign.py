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
        wires (array[int]): wires that the operator acts on
        n (array[int]) or int: binary array vector or integer value representing the state to flip the sign

    Raises:
        ValueError: "expected at integer binary array "
        ValueError: "expected at integer binary array for wires "
        ValueError: "expected at integer binary array not empty "
        ValueError: "expected at least one wire representing the qubit "

    .. seealso:: :func:`~.relevant_func`, :class:`~.RelevantClass` (optional)

    .. details::

        :title: Usage Details

        The template is used inside a qnode.
        The number of shots has to be explicitly set on the device when using sample-based measurements:

        .. code-block:: python

            dev = qml.device("default.qubit", wires=5, shots = 1000)

            @qml.qnode(dev)
            def circuit():
               for wire in list(range(5)):
                    qml.Hadamard(wires = wire)
               qml.FlipSign([1,0,1,0,0], wires = list(range(5)))
               for wire in list(range(5)):
                    qml.Hadamard(wires = wire)
               return qml.sample()

            drawer = qml.draw(circuit, show_all_wires = True)

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

        if type(n) == int:
            if n == 0:
                raise ValueError("expected at integer greater than zero for basic flipping state ")
            else:
                n = self.to_list(n)

        if np.array(n).dtype != np.dtype("int"):
            raise ValueError("expected at integer binary array ")

        if not isinstance(wires, list):
            raise ValueError("expected at integer array for wires ")

        if np.array(wires).dtype != np.dtype("int"):
            raise ValueError("expected a integer array for wires ")

        if len(wires) == 0:
            raise ValueError("expected at least one wire representing the qubit ")

        self._hyperparameters = {"n": n}
        super().__init__(wires=wires, do_queue=do_queue, id=id)

    @staticmethod
    def to_list(n):
        b_str = f"{n:b}".zfill(n)
        bin_list = [int(i) for i in b_str]
        return bin_list

    @property
    def num_params(self):
        return 0

    @staticmethod
    def compute_decomposition(wires, n):
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
                qml.ctrl(qml.PauliZ, control=wires[:-1], control_values=n[:-1])(
                    wires=wires[-1]
                )
            )

            if n[-1] == 0:
                op_list.append(qml.PauliX(wires[-1]))
        else:
            raise ValueError("Wires length and flipping state length does not match, they must be equal length ")

        return op_list
