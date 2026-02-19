#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <sstream>

#include "graphsim.h"
#include "loccliff.h"
#include "stabilizer.h"

namespace py = pybind11;

PYBIND11_MODULE(graphsim, m) {
    m.doc() = "Pybind11 bindings for GraphRegister";

    py::class_<GraphRegister>(m, "GraphRegister")
        .def(py::init<VertexIndex, int>(),
             py::arg("num_qubits"),
             py::arg("randomize") = -1)

        // Edge operations
        // .def("add_edge", &GraphRegister::add_edge)
        // .def("del_edge", &GraphRegister::del_edge)
        // .def("toggle_edge", &GraphRegister::toggle_edge)

        // Quantum gates
        .def("cphase", &GraphRegister::cphase)
        .def("cnot", &GraphRegister::cnot)

        // Measurements
        .def("measure",
            [](GraphRegister &gr,
               VertexIndex v,
               LocCliffOp basis,
               int force) {
                bool determined = false;
                int result = gr.measure(v, basis, &determined, force);
                return py::make_tuple(result, determined);
            },
            py::arg("vertex"),
            py::arg("basis"),
            py::arg("force") = -1)

        // Neighborhood inversion
        .def("invert_neighborhood",
             &GraphRegister::invert_neighborhood)

        // Pretty printing: return adjacency list as string
        .def("adj_list_str",
            [](const GraphRegister &gr) {
                std::ostringstream oss;
                gr.print_adj_list(oss);
                return oss.str();
            })

        // Pretty printing: stabilizer
        .def("stabilizer_str",
            [](const GraphRegister &gr) {
                std::ostringstream oss;
                gr.print_stabilizer(oss);
                return oss.str();
            });
}
