#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <sstream>

#include "graphsim.h"
#include "loccliff.h"
#include "stabilizer.h"

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
    m.doc() = "Pybind11 bindings for GraphRegister";

    py::class_<LocCliffOp>(m, "LocCliffOp")
        .def_readonly("op", &LocCliffOp::op)
        .def("__repr__", [](const LocCliffOp &lco) {
            return "<LocCliffOp op=" + std::to_string(lco.op) + ">";
        });

    // Expose LocCliffOp constants (structs, not enum)
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

        .def("print_stabilizers", [](const GraphRegister &gr) {
            std::ostringstream oss;
            gr.print_stabilizer(oss);
            return oss.str();
        });
}