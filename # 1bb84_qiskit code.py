# bb84_qiskit.py
# BB84 QKD demo using Qiskit (Aer simulator).
# Supports optional Eve (intercept-resend).
# Each photon is prepared and measured as a separate tiny circuit (shots=1).

import random
from qiskit import QuantumCircuit, Aer, execute

SIM_BACKEND = Aer.get_backend('qasm_simulator')

def prepare_circuit_for_bit(bit, basis):
    """
    Prepare a 1-qubit circuit representing Alice's encoding of 'bit' in 'basis'.
    basis: '+' or 'x'
    """
    qc = QuantumCircuit(1, 1)
    if bit == 1:
        qc.x(0)     # encode bit=1 in Z basis
    if basis == 'x':
        qc.h(0)     # rotate to X basis (|+> / |->)
    return qc

def measure_in_basis(qc, basis):
    """
    Add gates to measure the qubit in the chosen basis and measure into classical bit 0.
    This appends the measurement to the given circuit (which may already contain preparation).
    """
    if basis == 'x':
        qc.h(0)     # rotate X-basis states to Z basis for measurement
    qc.measure(0, 0)
    return qc

def run_single_shot(qc):
    """Execute the given 1-qubit circuit with shots=1 and return measured bit (0 or 1)."""
    job = execute(qc, SIM_BACKEND, shots=1)
    result = job.result()
    counts = result.get_counts()
    # counts is like {'0':1} or {'1':1}
    measured_bit = int(max(counts, key=counts.get))
    return measured_bit

def bb84_qiskit(n_bits=20, eve=False, seed=None):
    """
    Perform a BB84 run (simulation) with n_bits.
    If eve=True, simulate an intercept-resend Eve who measures each photon in a random basis then resends.
    Returns a dictionary with Alice/Bob sequences, matched indices, final keys, and QBER.
    """
    if seed is not None:
        random.seed(seed)

    # Step 1: Alice's random bits & bases
    alice_bits = [random.randint(0, 1) for _ in range(n_bits)]
    alice_bases = [random.choice(['+', 'x']) for _ in range(n_bits)]

    bob_bases = [random.choice(['+', 'x']) for _ in range(n_bits)]
    bob_results = []

    # If Eve present, generate her random bases
    if eve:
        eve_bases = [random.choice(['+', 'x']) for _ in range(n_bits)]
    else:
        eve_bases = [None] * n_bits

    # Process each photon individually (prepare -> possible Eve intercept -> Bob measure)
    for i in range(n_bits):
        # Alice prepares the photon
        alice_qc = prepare_circuit_for_bit(alice_bits[i], alice_bases[i])

        if eve:
            # Eve intercepts: measure alice_qc in Eve's basis
            eve_qc = alice_qc.copy()
            eve_qc = measure_in_basis(eve_qc, eve_bases[i])
            eve_result = run_single_shot(eve_qc)

            # Eve re-prepares a replacement photon according to her measured result and her basis,
            # then sends that to Bob (we emulate by making a new circuit)
            sent_qc = prepare_circuit_for_bit(eve_result, eve_bases[i])
        else:
            # No Eve: what Bob receives is exactly Alice's prepared photon
            sent_qc = alice_qc

        # Now Bob measures in his chosen basis
        bob_qc = sent_qc.copy()
        bob_qc = measure_in_basis(bob_qc, bob_bases[i])
        bob_result = run_single_shot(bob_qc)
        bob_results.append(bob_result)

    # Step 4: Sifting (keep positions where Alice and Bob used same basis)
    matched_indices = [i for i in range(n_bits) if alice_bases[i] == bob_bases[i]]
    alice_sift = [alice_bits[i] for i in matched_indices]
    bob_sift   = [bob_results[i] for i in matched_indices]

    # Step 5: Parameter estimation (sample a subset of the sifted bits to compute QBER)
    sample_size = max(1, int(0.25 * len(matched_indices))) if matched_indices else 0
    sample_positions = matched_indices[:sample_size]  # choose first k for demo simplicity
    sample_mismatches = sum(1 for i in sample_positions if alice_bits[i] != bob_results[i])
    qber = (sample_mismatches / sample_size) if sample_size > 0 else 0.0

    # Step 6: Final key (use remaining sifted bits after removing sample positions)
    key_positions = [i for i in matched_indices if i not in sample_positions]
    alice_key = [alice_bits[i] for i in key_positions]
    bob_key   = [bob_results[i] for i in key_positions]

    return {
        "alice_bits": alice_bits,
        "alice_bases": alice_bases,
        "bob_bases": bob_bases,
        "bob_results": bob_results,
        "eve_bases": eve_bases,
        "matched_indices": matched_indices,
        "sample_positions": sample_positions,
        "qber_sample": qber,
        "final_key_alice": alice_key,
        "final_key_bob": bob_key
    }

if _name_ == "_main_":
    # Example runs
    print("=== BB84 Qiskit demo: no Eve ===")
    out_no_eve = bb84_qiskit(n_bits=20, eve=False, seed=7)
    for k,v in out_no_eve.items():
        print(f"{k}: {v}")
    print("\n=== BB84 Qiskit demo: with Eve (intercept-resend) ===")
    out_eve = bb84_qiskit(n_bits=20, eve=True, seed=7)
    for k,v in out_eve.items():
        print(f"{k}: {v}")