import struct
import numpy as np
import graphsim
import pytest


def test_stabilizers_ghz():
    """Test a 3-qubit GHZ state (Star graph)"""
    gr = graphsim.GraphRegister(3)

    gr.H(0)
    gr.H(1)
    gr.H(2)

    gr.CZ(0, 1)
    gr.CZ(0, 2)

    assert gr.stabilizer_list() == ["+XZZ", "+ZXI", "+ZIX"]


def test_linear_cluster_4():
    """Test a 4-qubit linear chain: 0-1-2-3"""
    gr = graphsim.GraphRegister(4)
    for i in range(4):
        gr.H(i)

    gr.CZ(0, 1)
    gr.CZ(1, 2)
    gr.CZ(2, 3)

    # For a linear cluster, the stabilizer for qubit i is Z_{i-1} X_i Z_{i+1}
    expected = [
        "+XZII",  # Q0: X on 0, Z on neighbor 1
        "+ZXZI",  # Q1: X on 1, Z on neighbors 0, 2
        "+IZXZ",  # Q2: X on 2, Z on neighbors 1, 3
        "+IIZX",  # Q3: X on 3, Z on neighbor 2
    ]
    assert gr.stabilizer_list() == expected


def test_local_clifford_rotations():
    """Test how local gates (S, X) change the stabilizer representation"""
    gr = graphsim.GraphRegister(1)
    assert gr.stabilizer_list() == ["+Z"]

    gr.H(0)  # Starts in |+>, stabilizer is +X
    assert gr.stabilizer_list() == ["+X"]

    gr.S(0)  # S transforms X -> Y
    assert gr.stabilizer_list() == ["+Y"]

    gr.S(0)  # S again transforms Y -> -X
    assert gr.stabilizer_list() == ["-X"]


def test_disconnected_qubits():
    """Test qubits that have no edges between them"""
    gr = graphsim.GraphRegister(2)
    gr.H(0)
    gr.H(1)

    # No CZ gates, so stabilizers should just be X on each qubit
    assert gr.stabilizer_list() == ["+XI", "+IX"]


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

    assert np.allclose(gr.adjacency_matrix(), np.array([
        [0, 1, 1, 0],
        [1, 0, 0, 0],
        [1, 0, 0, 0],
        [0, 0, 0, 0],
    ]))


@pytest.mark.parametrize("id1", ["I", "X", "Y", "Z"])
@pytest.mark.parametrize("id2", ["A", "B", "C", "D", "E", "F"])
def test_apply_local_op(id1: str, id2: str):
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


def test_remove_edge():
    g = graphsim.GraphRegister(2)
    g.H(0)
    g.H(1)
    g.CZ(0, 1)
    g.del_edge(0, 1)

    assert g.adjacency_list() == [set(), set()]


def test_add_edge():
    g = graphsim.GraphRegister(2)
    g.add_edge(0, 1)

    assert g.adjacency_list() == [{1}, {0}]


def test_toggle_edge():
    g = graphsim.GraphRegister(2)
    g.toggle_edge(0, 1)

    assert g.adjacency_list() == [{1}, {0}]

    g.toggle_edge(0, 1)

    assert g.adjacency_list() == [set(), set()]


def test_force_measurement():
    g = graphsim.GraphRegister(1)
    g.H(0)
    assert g.measure(0, force=0, basis="Z") == 0

    g = graphsim.GraphRegister(1)
    g.H(0)
    assert g.measure(0, force=1, basis="Z") == 1


@pytest.mark.parametrize(
    "gatename",
    [
        ("X", (2,)),
        ("Z", (2,)),
        ("S", (2,)),
        ("H", (2,)),
        ("CX", (2, 3)),
        ("CZ", (2, 3)),
    ],
)
def test_out_of_bounds(gatename: tuple[str, tuple[int]]):
    g = graphsim.GraphRegister(2)
    with pytest.raises(IndexError) as e:
        getattr(g, gatename[0])(*gatename[1])
    assert e.type is IndexError

def test_merge():
    a = graphsim.GraphRegister(5)
    a.H(0)
    a.H(1)
    a.H(2)
    a.CZ(0, 1)
    a.CZ(0, 2)
    a.add_edge(0, 1)
    a.add_edge(0, 2)

    b = graphsim.GraphRegister(3)
    b.add_edge(0, 1)
    b.S(0)
    b.S(0)
    b.S(2)
    
    c = a + b # a.merge(b)

    assert np.allclose(b.adjacency_matrix(), c.adjacency_matrix()[-len(b):, -len(b):])
    assert b.stabilizer_list() == [sign[0]+p[-len(b):] for p, sign in zip(c.stabilizer_list()[-len(b):], b.stabilizer_list(), strict=True)]
    
    assert np.allclose(a.adjacency_matrix(), c.adjacency_matrix()[:len(a), :len(a)])
    assert a.stabilizer_list() == [p[:len(a)+1] for p in c.stabilizer_list()[:len(a)]]
