#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <sstream>

#include "graphsim.h"
#include "loccliff.h"
#include "stabilizer.h"
#include "loccliff.h"

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
    m.doc() = "Pybind11 bindings for GraphSim";

    py::class_<LocCliffOp>(m, "LocCliffOp", "Class representing a Local Clifford Operator.")
        .def(py::init<unsigned short>(),
            py::arg("op"),
            "Construct by its assigned integer.")

        .def(py::init<unsigned short, unsigned short>(),
            py::arg("signsymb"),
            py::arg("permsymb"),
            R"doc(
            Construct from Pauli and permutation integers.

            Args:
                signsymb (int): A Pauli integer representing "I", "X", "Y" or "Z" in the range [0, 3].
                permsymb (int): A permutation integer in the range [0, 5].
            )doc")

        .def(py::init([](const std::string &s) {
            if (s.size() != 2)
                throw std::runtime_error("Input must be 2 characters");
            
            unsigned short signsymb;
            switch (s[0]) {
                case 'I': signsymb = 0; break;
                case 'X': signsymb = 1; break;
                case 'Y': signsymb = 2; break;
                case 'Z': signsymb = 3; break;
                default:
                    throw std::runtime_error("First character must be I, X, Y, Z");
            }

            unsigned short permsymb;
            switch (s[1]) {
                case 'A': permsymb = 0; break;
                case 'B': permsymb = 1; break;
                case 'C': permsymb = 2; break;
                case 'D': permsymb = 3; break;
                case 'E': permsymb = 4; break;
                case 'F': permsymb = 5; break;
                default:
                    throw std::runtime_error("Second character must be A, B, C, D, E, F");
            }

            return LocCliffOp(signsymb, permsymb);
        }), py::arg("s"), "Construct from string representation (e.g. 'IA').")

        .def("get_name", &LocCliffOp::get_name, "Get the string representation of the operator.")

        .def("conjugate", &LocCliffOp::conjugate,
             py::arg("trans"), "Conjugate the operator by another Local Clifford Operator.")

        .def("herm_adjoint", &LocCliffOp::herm_adjoint, "Get the Hermitian adjoint of the operator.")

        .def_static("mult_phase",
             &LocCliffOp::mult_phase,
             py::arg("op1"),
             py::arg("op2"))

        .def("isXY", &LocCliffOp::isXY, "Check if the operator is X or Y type.")

        .def("is_diagonal", &LocCliffOp::is_diagonal, "Check if the operator is diagonal.")

        .def("get_matrix", [](const LocCliffOp &self) {
            RightMatrix rm = self.get_matrix();

            std::complex<float> scale = rm.sqrt2norm ? 1.0f / std::sqrt(2.0f) : 1.0f;
            py::array_t<std::complex<float>> arr({2,2});

            auto buf = arr.mutable_unchecked<2>();

            // Global phase: e^{-i*pi/4}
            const std::complex<float> global_phase = {1.0f/std::sqrt(2.0f), -1.0f/std::sqrt(2.0f)};

            // Only apply global phase if loc.op == 4 or 7 (See Simon Anders' thesis)
            scale = (self.op == 4 || self.op == 7) ? scale * global_phase : scale;

            for (py::ssize_t i = 0; i < 2; i++) {
                for (py::ssize_t j = 0; j < 2; j++) {
                    float ampl = rm.ampls[i][j] ? 1.0f : 0.0f;
                    std::complex<float> phase_value;

                    switch (rm.phases[i][j].ph & 0x03) {
                        case 0: phase_value = std::complex<float>(1.0f, 0.0f); break;  // 0 -> 1
                        case 1: phase_value = std::complex<float>(0.0f, 1.0f); break;  // 1 -> i
                        case 2: phase_value = std::complex<float>(-1.0f, 0.0f); break; // 2 -> -1
                        case 3: phase_value = std::complex<float>(0.0f, -1.0f); break; // 3 -> -i
                    }

                    buf(i, j) = ampl * phase_value * scale;
                }
            }
            return arr;
        }, "Get the matrix representation of the operator.")

        .def_readwrite("op", &LocCliffOp::op)

        .def("__repr__", [](const LocCliffOp &self) {
            return "<LocCliffOp Id: "+ std::to_string(self.op)+" Name: "+ self.get_name() + ">";
        });

    m.attr("lco_X") = py::cast(lco_X);
    m.attr("lco_Y") = py::cast(lco_Y);
    m.attr("lco_Z") = py::cast(lco_Z);
    m.attr("lco_H") = py::cast(lco_H);
    m.attr("lco_S") = py::cast(lco_S);

    py::class_<GraphRegister>(m, "GraphRegister", "A quantum register representing a graph state and local Clifford operators.")
        .def(py::init([](VertexIndex num_qubits, int randomize) {
                if (num_qubits == 0) {
                    throw py::value_error("num_qubits must be greater than 0");
                }
                return std::make_unique<GraphRegister>(num_qubits, randomize);
            }),
            py::arg("num_qubits"),
            py::arg("randomize") = -1,
            "Initialize a quantum register with 'num_qubits' qubits."
        )

        // Edge operations
        .def("add_edge", &GraphRegister::add_edge, "Add an edge between two vertices.")
        .def("del_edge", &GraphRegister::del_edge, "Delete an edge between two vertices.")
        .def("toggle_edge", &GraphRegister::toggle_edge, "Toggle an edge between two vertices.")

        // Quantum gates
        .def("H", &GraphRegister::hadamard, "Apply Hadamard gate to a vertex.")
        .def("S", &GraphRegister::phaserot, "Apply Phase rotation (S gate) to a vertex.")
        .def("X", &GraphRegister::bitflip, "Apply Bit flip (X gate) to a vertex.")
        .def("Z", &GraphRegister::phaseflip, "Apply Phase flip (Z gate) to a vertex.")
        .def("CZ", &GraphRegister::cphase, "Apply Controlled-Phase (CZ) gate between two vertices.")
        .def("CX", &GraphRegister::cnot, "Apply Controlled-NOT (CX) gate between control and target vertices.")
        .def("VOP", &GraphRegister::local_op, "Apply a local Clifford operation to a vertex.")

        .def(
            "measure",
            [](GraphRegister &gr, VertexIndex v, int force, char basis) {
                LocCliffOp lco_basis = lco_Z;

                switch (basis){
                    case 'X':
                        lco_basis = lco_X; break;
                    case 'Y':
                        lco_basis = lco_Y; break;
                    case 'Z':
                        lco_basis = lco_Z; break;
                    default:
                        throw std::invalid_argument("basis must be 'X', 'Y', or 'Z'");
                }
                return gr.measure(v, lco_basis, nullptr, force);
            },
                py::arg("vertex"),
                py::arg("force") = -1,
                py::arg("basis") = "Z",
                "Measure a qubit in the specified basis (X, Y, or Z).")

        // Neighborhood inversion
        .def("invert_neighborhood", &GraphRegister::invert_neighborhood, "Invert the neighborhood of a vertex (Local Complementation).")

        // Pybindings for exporting the data
        .def("stabilizer_list", &GraphRegister::stabilizer_list, "Get the list of stabilizer generators.")

        .def("adjacency_matrix", &GraphRegister::adjacency_matrix, "Get the adjacency matrix of the graph.")

        .def("adjacency_list", &GraphRegister::adjacency_list, "Get the adjacency list of the graph.")

        .def("vop_list", &GraphRegister::vop_list, "Get the list of local Clifford operators.")

        // Debug
        .def("print_adjacency_list",
             [](const GraphRegister &gr) {
                 std::ostringstream oss;
                 gr.print_adj_list(oss);
                 return oss.str();
             }, "Return the adjacency list as a string.")
        
        .def("__repr__", [](const GraphRegister &gr) {
            std::ostringstream oss;
            oss << "<GraphRegister>" << std::endl;
            oss << "Adjacency List: " << std::endl;
            gr.print_adj_list(oss);
            return oss.str();
        });
}