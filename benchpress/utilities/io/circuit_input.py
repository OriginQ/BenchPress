# This code is part of Qiskit.
#
# (C) Copyright IBM 2024.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
"""QASMbench utilities"""

from benchpress.config import Configuration


def input_circuit_properties(circuit, benchmark):
    """Return input circuit statistics

    circuit : Input quantum circuit
    benchmark (Benchmark): Benchmark class to record info to

    """
    gym_name = Configuration.gym_name
    if gym_name in ["qiskit", "qiskit-ibm-transpiler"]:
        from benchpress.qiskit_gym.utils.io import qiskit_input_circuit_properties

        qiskit_input_circuit_properties(circuit, benchmark)

    elif gym_name == "tket":
        from benchpress.tket_gym.utils.io import tket_input_circuit_properties

        tket_input_circuit_properties(circuit, benchmark)

    elif gym_name == "bqskit":
        from benchpress.bqskit_gym.utils.io import bqskit_input_circuit_properties

        bqskit_input_circuit_properties(circuit, benchmark)

    elif gym_name == "staq":
        from benchpress.staq_gym.utils.io import staq_input_circuit_properties

        staq_input_circuit_properties(circuit, benchmark)

    elif gym_name == "braket":
        from benchpress.braket_gym.utils.io import braket_input_circuit_properties

        braket_input_circuit_properties(circuit, benchmark)

    elif gym_name == "cirq":
        from benchpress.cirq_gym.utils.io import cirq_input_circuit_properties

        cirq_input_circuit_properties(circuit, benchmark)
    elif gym_name == "qpanda":
        from benchpress.qpanda_gym.utils.io import qpanda_input_circuit_properties

        qpanda_input_circuit_properties(circuit, benchmark)
    else:
        raise Exception(f"Unsupported gym name {gym_name}")
