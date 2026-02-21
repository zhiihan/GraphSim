import graphsim
import random
import numpy as np

# we need a quantum register with 7 qubits:
gr = graphsim.GraphRegister(5)

gr.hadamard(0)
gr.hadamard(1)
gr.hadamard(2)
gr.hadamard(3)
gr.cphase(0, 1)
gr.cphase(0, 2)
gr.cphase(0, 3)
gr.cphase(0, 4)

print(gr.adj_list_str(), gr.stabilizer_str())
print(gr.adjacency_matrix_numpy())

gr.hadamard(0)

print(gr.measure(0), gr.measure(1), gr.measure(2), gr.measure(3), gr.measure(4))
