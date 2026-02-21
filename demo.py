import graphsim

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

print(gr.adjacency_matrix())
print(gr.adjacency_list())
print(gr.vop_list())
print(gr.stabilizer_str())

gr.hadamard(0)

print(gr.measure(0), gr.measure(1), gr.measure(2), gr.measure(3), gr.measure(4))
