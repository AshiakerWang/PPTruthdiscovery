def verify(self, input_vector, expected_output_vector):
    assert len(input_vector) == self.input_size 
    assert len(expected_output_vector) == self.output_size 
    actual_output_vector = self.evaluate(input_vector)
    if actual_output_vector == expected_output_vector:
        print(" True ")
    else:
        print(" False ")
    leak = False
    for i in range(self.input_size): 
        value = input_vector[i]
        k0, k1, b = self.garbled_input[i]
        if value == int.from_bytes(b, "big"):
            leak = True
            print(f"Input wire {i} leaks its value {value}.")
    for i in range(self.num_wires - self.output_size, self.num_wires):
        value = actual_output_vector[i - (self.num_wires - self.output_size)]
        k0, k1, b = self.garbled_output[i]
        if value == int.from_bytes(b, "big"):
            leak = True
            print(f"Output wire {i} leaks its value {value}.")
    if not leak:
        print("No information leakage detected.")
gc = GarbledCircuit([("AND", 0, 1, 3), ("NOT", 2, 4, 5), ("OR", 3, 5, 6)])
gc.garble()
input_vector = [1, 0, 1]
expected_output_vector = [0]
gc.verify(input_vector, expected_output_vector)
