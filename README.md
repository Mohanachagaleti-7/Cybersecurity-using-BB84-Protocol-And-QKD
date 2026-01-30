# Cybersecurity-using-BB84-Protocol-And-QKD
About This project implements the BB84 Quantum Key Distribution (QKD) protocol — a secure cryptographic method that uses the principles of quantum mechanics to generate and share encryption keys between two parties. BB84 ensures that any attempt at eavesdropping can be detected due to quantum measurement disturbance.
# How BB84 Works (Quick)
1) Prepare: Alice encodes random bits using two bases: rectilinear (+) and diagonal (×).

2) Send: Qubits go over the quantum channel. Any measurement disturbs them.

3) Measure: Bob measures each qubit in a random basis (+/×).

4) Sift: Over a public channel, they reveal only bases and keep positions where they matched.

5) Check: They sample a portion of the raw key to estimate QBER (error rate).

6) Detect: High QBER ⇒ likely eavesdropping. Low QBER ⇒ keep the rest as a shared secret.

7) Use: Apply the secret bits as a one‑time pad to encrypt/decrypt messages
