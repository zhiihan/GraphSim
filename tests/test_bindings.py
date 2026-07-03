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
    "opname",
    [
        ("measure", (2,)),
        ("invert_neighborhood", (2,)),
        ("local_complementation", (2,)),
    ],
)
def test_out_of_bounds(opname: tuple[str, tuple[int]]):
    g = graphsim.GraphRegister(2)
    with pytest.raises(IndexError) as e:
        getattr(g, opname[0])(*opname[1])
    assert e.type is IndexError

def test_auto_expand_edges():
    g = graphsim.GraphRegister(2)
    g.add_edge(2, 4)
    assert len(g) == 5
    assert g.adjacency_list() == [set(), set(), {4}, set(), {2}]

    g = graphsim.GraphRegister(2)
    g.del_edge(2, 4)
    assert len(g) == 5
    assert g.adjacency_list() == [set(), set(), set(), set(), set()]

    g = graphsim.GraphRegister(2)
    g.toggle_edge(2, 4)
    assert len(g) == 5
    assert g.adjacency_list() == [set(), set(), {4}, set(), {2}]

def test_default_constructor():
    g = graphsim.GraphRegister()
    assert len(g) == 0
    assert g.num_qubits() == 0

def test_auto_expand_gates():
    g = graphsim.GraphRegister()
    g.H(3)
    assert len(g) == 4
    assert g.vop_list()[3] == "IA" # H * H = I (Since QubitVertex initializes with H, H on 3 changes its VOP to H*H = I, i.e., "IA")

    g = graphsim.GraphRegister(2)
    g.CZ(2, 5)
    assert len(g) == 6

    g = graphsim.GraphRegister(2)
    g.CX(5, 1)
    assert len(g) == 6

    g = graphsim.GraphRegister(2)
    g.H(4)
    g.VOP(4, graphsim.LocCliffOp("XA"))
    assert g.vop_list()[4] == "XA"
    assert len(g) == 5

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
    assert a.stabilizer_list() == [p[:len(a)+1] for p in c.stabilizer_list()[:len(a)]] # These are different because there is a sign, e.g. '+IXX'


def test_zero_size_register():
    gr = graphsim.GraphRegister(0)
    assert len(gr) == 0
    assert gr.num_qubits() == 0
    assert gr.stabilizer_list() == []
    assert gr.adjacency_list() == []
    assert gr.vop_list() == []
    assert gr.adjacency_matrix().shape == (0, 0)
    
    # Check that merge works
    gr2 = graphsim.GraphRegister(2)
    merged = gr + gr2
    assert len(merged) == 2
    
    merged2 = gr2 + gr
    assert len(merged2) == 2

def test_negative_size_register():
    with pytest.raises(TypeError):
        graphsim.GraphRegister(-1)
    
    with pytest.raises(TypeError):
        graphsim.GraphRegister(2.5)

def test_local_complementation_only_edges():
    # Setup a state 1 - 0 - 2
    g = graphsim.GraphRegister(3)
    g.H(0)
    g.H(1)
    g.H(2)
    g.CZ(0, 1)
    g.CZ(0, 2)
    
    # Save the original VOPs
    original_vops = g.vop_list()
    
    # Perform local complementation on 0
    g.local_complementation(0)
    
    # Check edges: 1 and 2 should now be connected
    assert g.adjacency_list() == [{1, 2}, {0, 2}, {0, 1}]
    
    # Check VOPs: should be unchanged
    assert g.vop_list() == original_vops
    
    # Compare with invert_neighborhood (which adjusts VOPs)
    g2 = graphsim.GraphRegister(3)
    g2.H(0)
    g2.H(1)
    g2.H(2)
    g2.CZ(0, 1)
    g2.CZ(0, 2)
    g2.invert_neighborhood(0)
    
    # Adjacencies should be the same
    assert g2.adjacency_list() == g.adjacency_list()
    # VOPs should be different (adjusted)
    assert g2.vop_list() != original_vops

def test_identity_gate():
    g = graphsim.GraphRegister(2)
    g.I(4)
    assert len(g) == 5