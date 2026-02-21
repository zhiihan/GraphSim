cmake_minimum_required(VERSION 3.15)
project("graphsim" LANGUAGES CXX)

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)

include_directories(src)

# Add all source files that contain the method implementations
set(SOURCES
    src/bindings.cpp
    src/graphsim.cpp      
    src/loccliff.cpp
    src/stabilizer.cpp
)

# Build the Python module
pybind11_add_module(_core MODULE ${SOURCES})

install(TARGETS _core DESTINATION "graphsim")
