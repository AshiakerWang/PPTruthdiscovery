def evaluate(self, input_vector):
    assert len(input_vector) == self.input_size 
    wire_keys = {}
    for i in range(self.input_size):
        value = input_vector[i] 
        k0, k1, b = self.garbled_input[i] 
        wire_keys[i] = k0 if value == 0 else k1
    def xor_encrypt(key, message):
        return bytes(x ^ y for x, y in zip(key, message))
    def hash(x, y):
        return hashlib.sha256(x + y).digest()[:KEY_SIZE]
    for gate in self.circuit:
        gate_type, *wires = gate 
        assert gate_type in GATE_TYPES 
        assert len(wires) == 2 or (gate_type == "NOT" and len(wires) == 3) 
        kx = wire_keys[wires[0]] 
        bx = self.garbled_input[wires[0]][-1] 
        if gate_type != "NOT":
            ky = wire_keys[wires[1]] 
            by = self.garbled_input[wires[1]][-1] 
            kz0, kz1, bz = self.garbled_output[wires[-1]] 
        table = self.garbled_circuit.pop(0) 
        if gate_type == "NOT":
            index = 0 if bx == COLOR_BITS[0] else 1
        else:
            
            index = 0 if bx == COLOR_BITS[0] and by == COLOR_BITS[0] else \
                    1 if bx == COLOR_BITS[0] and by == COLOR_BITS[1] else \
                    2 if bx == COLOR_BITS[1] and by == COLOR_BITS[0] else \
                    3
        ciphertext = table[index]
        
        if ciphertext == ZERO:
            ciphertext = hash(kx, ky) if gate_type != "NOT" else hash(kx, ZERO)
        output_key = xor_encrypt(hash(kx, ky) if gate_type != "NOT" else hash(kx, ZERO), ciphertext)
        if gate_type == "NOT":
            output_key, output_key2 = output_key[:KEY_SIZE], output_key[KEY_SIZE:]
        wire_keys[wires[-1]] = output_key
        if gate_type == "NOT":
            wire_keys[wires[-2]] = output_key2
    output_vector = []
    for i in range(self.num_wires - self.output_size, self.num_wires):
        key = wire_keys[i] 
        k0, k1, b = self.garbled_output[i] 
        value = 0 if (key == k0 and bz == COLOR_BITS[0]) or (key == k1 and bz == COLOR_BITS[1]) else 1
        output_vector.append(value)
    return output_vector
