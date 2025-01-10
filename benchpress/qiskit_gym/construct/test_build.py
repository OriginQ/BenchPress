"""Test circuit generation"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QuantumVolume
from qiskit.circuit.library import EfficientSU2
from qiskit.qasm2 import load

from benchpress.config import Configuration
from benchpress.workouts.validation import benchpress_test_validation
from benchpress.workouts.build import WorkoutCircuitConstruction
from benchpress.utilities.io import output_circuit_properties
from benchpress.qiskit_gym.circuits import (
    dtc_unitary,
    multi_control_circuit,
    random_clifford_circuit,
)

SEED = 12345


@benchpress_test_validation
class TestWorkoutCircuitConstruction(WorkoutCircuitConstruction):
    def test_QV100_build(self, benchmark):
        """Measures an SDKs ability to build a 100Q
        QV circuit from scratch.
        """

        @benchmark
        def result():
            out = QuantumVolume(100, 100, seed=SEED)
            # circuit = QuantumCircuit(2)
            # real_part = np.random.rand(4, 4)
            # imag_part = np.random.rand(4, 4)
            # nmatrix = real_part + 1j * imag_part
            # circuit.unitary(nmatrix,[0,1])
            return out

        assert result

    def test_DTC100_set_build(self, benchmark):
        """Measures an SDKs ability to build a set
        of 100Q DTC circuits out to 100 layers of
        the underlying unitary
        """

        @benchmark
        def result():
            max_cycles = 100
            num_qubits = 100
            initial_state = QuantumCircuit(num_qubits)
            dtc_circuit = dtc_unitary(num_qubits, g=0.95, seed=SEED)

            circs = [initial_state]
            for tt in range(max_cycles):
                qc = circs[tt].compose(dtc_circuit)
                circs.append(qc)
            return circs[-1]

        output_circuit_properties(result, "rzz", benchmark)
        assert result.count_ops()["rzz"] == 9900

    def test_multi_control_circuit(self, benchmark):
        """Measures an SDKs ability to build a circuit
        with a multi-controlled X-gate
        """
        ITER_CIRCUIT_WIDTH = 16

        @benchmark
        def result():
            out = multi_control_circuit(ITER_CIRCUIT_WIDTH)
            return out

        assert result

    def test_clifford_build(self, benchmark):
        """Measures an SDKs ability to build a 100Q
        Clifford circuit from scratch.
        """

        @benchmark
        def result():
            random_clifford_circuit(100, seed=SEED)
            return True

        assert result

    def test_param_circSU2_100_build(self, benchmark):
        """Measures an SDKs ability to build a
        parameterized efficient SU2 circuit with circular entanglement
        over 100Q utilizing 4 repetitions.  This will yield a
        circuit with 1000 parameters
        """
        N = 100

        @benchmark
        def result():
            out = EfficientSU2(N, reps=4, entanglement="circular", flatten=True)
            out._build()
            return out

        assert result.num_parameters == 1000

    def test_param_circSU2_100_bind(self, benchmark):
        """Measures an SDKs ability to bind 1000 parameters
        to efficient SU2 circuit over 100Q with circular
        entanglement and 4 repetitions.
        """
        N = 100
        qc = EfficientSU2(N, reps=4, entanglement="circular", flatten=True)
        assert qc.num_parameters == 1000
        params = np.linspace(0, 2 * np.pi, qc.num_parameters)

        @benchmark
        def result():
            out = qc.assign_parameters(params)
            return out

        assert result.num_parameters == 0

    def test_QV100_qasm2_import(self, benchmark):
        """QASM import of QV100 circuit"""

        @benchmark
        def result():
            out = load(Configuration.get_qasm_dir("qv") + "qv_N100_12345.qasm")
            return out

        output_circuit_properties(result, "cx", benchmark)
        ops = result.count_ops()
        assert ops.get("rz", 0) == 120000
        assert ops.get("rx", 0) == 80000
        assert ops.get("cx", 0) == 15000

    def test_bigint_qasm2_import(self, benchmark):
        """bigint QASM import test"""

        @benchmark
        def result():
            out = load(Configuration.get_qasm_dir("bigint") + "bigint.qasm")
            return out

        output_circuit_properties(result, "cx", benchmark)
        assert result
