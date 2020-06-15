#include "pythonHelpers.hpp"
#include <stdlib.h>

namespace scorepy
{
const char* get_module_name(const PyFrameObject& frame)
{
    PyObject* module_name = PyDict_GetItemString(frame.f_globals, "__name__");
    if (module_name)
        return PyUnicode_AsUTF8(module_name);

    // this is a NUMPY special situation, see NEP-18, and Score-P issue #63
    // TODO: Use string_view/C-String to avoid creating 2 std::strings
    const char* filename = PyUnicode_AsUTF8(frame.f_code->co_filename);
    if (filename && (std::string(filename) == "<__array_function__ internals>"))
        return "numpy.__array_function__";
    else
        return "unkown";
}

std::string get_file_name(const PyFrameObject& frame)
{
    PyObject* filename = frame.f_code->co_filename;
    if (filename == Py_None)
    {
        return "None";
    }
    char actual_path[PATH_MAX];
    const char* full_file_name = realpath(PyUnicode_AsUTF8(filename), actual_path);
    return full_file_name ? full_file_name : "ErrorPath";
}
} // namespace scorepy
