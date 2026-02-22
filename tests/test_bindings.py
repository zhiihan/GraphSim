import graphsim
import pytest


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

@pytest.mark.parametrize("id1", ['I', 'X', 'Y', 'Z'])
@pytest.mark.parametrize("id2", ['A', 'B', 'C', 'D', 'E', 'F'])
def test_apply_local_op(id1 : str, id2 : str):
    local_op_id = id1 + id2

    g = graphsim.GraphRegister(1)
    g.H(0)

    g.VOP(0, graphsim.LocCliffOp(local_op_id))
    assert g.vop_list()[0] == local_op_id


# Skipping because don't know why cibuildwheel takes so long to install stim
@pytest.mark.skip
def test_vs_stim():
    import stim 

    gr = graphsim.GraphRegister(2)
    gr.H(0)
    gr.S(0)
    gr.CX(0, 1)
    gr.S(0)
    gr.S(0)

    stab_list = (
        stim.Circuit("""
    H 0
    S 0
    CX 0 1
    S 0
    S 0
    """)
        .to_tableau()
        .to_stabilizers()
    )

    stab_list = list(map(str, stab_list))

    assert gr.stabilizer_list() == stab_list
