import graphsim


def test_stabilizers():
    gr = graphsim.GraphRegister(3)

    gr.H(0)
    gr.H(1)
    gr.H(2)

    gr.CZ(0, 1)
    gr.CZ(0, 2)

    assert gr.stabilizer_list() == ["+XZZ", "+ZXI", "+ZIX"]


def test_adjacency_list():
    gr = graphsim.GraphRegister(4)

    gr.H(0)
    gr.H(1)
    gr.H(2)
    gr.H(3)

    gr.CZ(0, 1)
    gr.CZ(0, 2)

    assert gr.adjacency_list() == [{1, 2}, {0}, {0}, set()]


def test_adjacency_matrix():
    gr = graphsim.GraphRegister(4)

    gr.H(0)
    gr.H(1)
    gr.H(2)
    gr.H(3)

    gr.CZ(0, 1)
    gr.CZ(0, 2)

    assert gr.adjacency_matrix() == [
        [0, 1, 1, 0],
        [1, 0, 0, 0],
        [1, 0, 0, 0],
        [0, 0, 0, 0],
    ]
