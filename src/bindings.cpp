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
    m.doc() = "Pybind11 bindings for GraphRegister";

    py::class_<LocCliffOp>(m, "LocCliffOp")
        .def(py::init<unsigned short>(),
             py::arg("op"))

        .def(py::init<unsigned short, unsigned short>(),
             py::arg("signsymb"),
             py::arg("permsymb"))

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
        }))

        .def("get_name", &LocCliffOp::get_name)

        .def("conjugate", &LocCliffOp::conjugate,
             py::arg("trans"))

        .def("herm_adjoint", &LocCliffOp::herm_adjoint)

        .def_static("mult_phase",
             &LocCliffOp::mult_phase,
             py::arg("op1"),
             py::arg("op2"))

        .def("isXY", &LocCliffOp::isXY)

        .def("is_diagonal", &LocCliffOp::is_diagonal)

        .def("get_matrix", [](const LocCliffOp &self) {
            RightMatrix rm = self.get_matrix();

            std::complex<float> scale = rm.sqrt2norm ? 1.0f / std::sqrt(2.0f) : 1.0f;
            py::array_t<std::complex<float>> arr({2,2});

            py::array_t<std::complex<float>> arr2({2,2});

            auto buf = arr.mutable_unchecked<2>();

            auto buf2 = arr2.mutable_unchecked<2>();

            // Global phase: e^{-i*pi/4}
            const std::complex<float> global_phase = {1.0f/std::sqrt(2.0f), -1.0f/std::sqrt(2.0f)};

            // Only apply global phase if loc.op == 4 or 7 (See Simon Anders' thesis)
            scale = (self.op == 4 || self.op == 7) ? scale * global_phase : scale;

            for (ssize_t i = 0; i < 2; i++) {
                for (ssize_t j = 0; j < 2; j++) {
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
        })

        .def_readwrite("op", &LocCliffOp::op)

        .def("__repr__", [](const LocCliffOp &self) {
            return "<LocCliffOp Id: "+ std::to_string(self.op)+" Name: "+ self.get_name() + ">";
        });

    m.attr("lco_X") = py::cast(lco_X);
    m.attr("lco_Y") = py::cast(lco_Y);
    m.attr("lco_Z") = py::cast(lco_Z);
    m.attr("lco_H") = py::cast(lco_H);
    m.attr("lco_S") = py::cast(lco_S);

    py::class_<GraphRegister>(m, "GraphRegister")
        .def(py::init<VertexIndex, int>(), py::arg("num_qubits"),
             py::arg("randomize") = -1)

        // Edge operations
        // .def("add_edge", &GraphRegister::add_edge)
        // .def("del_edge", &GraphRegister::del_edge)
        // .def("toggle_edge", &GraphRegister::toggle_edge)

        // Quantum gates
        .def("H", &GraphRegister::hadamard)
        .def("S", &GraphRegister::phaserot)
        .def("X", &GraphRegister::bitflip)
        .def("Z", &GraphRegister::phaseflip)
        .def("CZ", &GraphRegister::cphase)
        .def("CX", &GraphRegister::cnot)

        .def(
            "measure",
            [](GraphRegister &gr, VertexIndex v) {
                // call C++ measure with defaults: basis = lco_Z, determined =
                // nullptr, force = -1
                int result = gr.measure(v, lco_Z, NULL, -1);
                return result;
            },
            py::arg("vertex"))

        // Neighborhood inversion
        .def("invert_neighborhood", &GraphRegister::invert_neighborhood)

        // Pybindings for exporting the data
        .def("stabilizer_list", &GraphRegister::stabilizer_list)

        .def("adjacency_matrix", &GraphRegister::adjacency_matrix)

        .def("adjacency_list", &GraphRegister::adjacency_list)

        .def("vop_list", &GraphRegister::vop_list)

        // Debug
        .def("print_adjacency_list",
             [](const GraphRegister &gr) {
                 std::ostringstream oss;
                 gr.print_adj_list(oss);
                 return oss.str();
             })
        
        .def("__repr__", [](const GraphRegister &gr) {
            std::ostringstream oss;
            oss << "<GraphRegister>" << std::endl;
            oss << "Adjacency List: " << std::endl;
            gr.print_adj_list(oss);
            return oss.str();
        });
}