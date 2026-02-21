import graphsim

# we need a quantum register with 7 qubits:
gr = graphsim.GraphRegister(5)

gr.H(0)
gr.H(1)
gr.H(2)
gr.H(3)
gr.CZ(0, 1)
gr.CZ(0, 2)
gr.CZ(0, 3)
gr.CZ(0, 4)

print(gr.adjacency_matrix())
print(gr.adjacency_list())
print(gr.vop_list())
print(gr.stabilizer_list())

gr.H(0)

print(gr.measure(0), gr.measure(1), gr.measure(2), gr.measure(3), gr.measure(4))
