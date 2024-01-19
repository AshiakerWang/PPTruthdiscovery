import random
import hashlib
import secrets

KEY_SIZE = 16 
GATE_TYPES = ["AND", "OR", "XOR", "NOT"] 
COLOR_BITS = [b"\x00", b"\x01"]
ZERO = b"\x00" * KEY_SIZE 

class GarbledCircuit:
    def __init__(self, circuit):
        self.circuit = circuit
        self.num_wires = max(max(gate[1:]) for gate in circuit) + 1 
        self.num_gates = len(circuit) 
        self.input_size = min(gate[1] for gate in circuit) 
        self.output_size = self.num_wires - max(gate[-1] for gate in circuit) - 1 
        self.garbled_circuit = [] 
        self.garbled_input = {} 
        self.garbled_output = {} 

    def garble(self):
        for i in range(self.num_wires):
            k0 = secrets.token_bytes(KEY_SIZE) 
            k1 = secrets.token_bytes(KEY_SIZE) 
            b = random.choice(COLOR_BITS) 
            self.garbled_input[i] = (k0, k1, b) 
            self.garbled_output[i] = (k0, k1, b) 
        for gate in self.circuit:
            gate_type, *wires = gate 
            assert gate_type in GATE_TYPES 
            assert len(wires) == 2 or (gate_type == "NOT" and len(wires) == 3) 
            kx0, kx1, bx = self.garbled_input[wires[0]]
            ky0, ky1, by = self.garbled_input[wires[1]]
            kz0, kz1, bz = self.garbled_output[wires[-1]]
            def xor_encrypt(key, message):
                return bytes(x ^ y for x, y in zip(key, message))
            def hash(x, y):
                return hashlib.sha256(x + y).digest()[:KEY_SIZE]
            if gate_type == "AND":
                c00 = xor_encrypt(hash(kx0, ky0), kz0) 
                c01 = xor_encrypt(hash(kx0, ky1), kz0) 
                c10 = xor_encrypt(hash(kx1, ky0), kz0) 
                c11 = xor_encrypt(hash(kx1, ky1), kz1) 
            elif gate_type == "OR":
                c00 = xor_encrypt(hash(kx0, ky0), kz0) 
                c01 = xor_encrypt(hash(kx0, ky1), kz1) 
                c10 = xor_encrypt(hash(kx1, ky0), kz1) 
                c11 = xor_encrypt(hash(kx1, ky1), kz1) 
            elif gate_type == "XOR":
                c00 = xor_encrypt(hash(kx0, ky0), kz0) 
                c01 = xor_encrypt(hash(kx0, ky1), kz1) 
                c10 = xor_encrypt(hash(kx1, ky0), kz1) 
                c11 = xor_encrypt(hash(kx1, ky1), kz0) 
            elif gate_type == "NOT":
                c0 = xor_encrypt(hash(kx0, ZERO), kx0 + kz1) 
                c1 = xor_encrypt(hash(kx1, ZERO), kx1 + kz0) 
            if gate_type == "NOT":
                if bx == COLOR_BITS[0]:
                    table = [c0, c1]
                else:
                    table = [c1, c0]
            else:
                if bx == COLOR_BITS[0] and by == COLOR_BITS[0]:
                    table = [c00, c01, c10, c11]
                elif bx == COLOR_BITS[0] and by == COLOR_BITS[1]:
                    table = [c01, c00, c11, c10]
                elif bx == COLOR_BITS[1] and by == COLOR_BITS[0]:
                    table = [c10, c11, c00, c01]
                else:
                    table = [c11, c10, c01, c00]
            table[0] = ZERO
            self.garbled_circuit.append(table)
