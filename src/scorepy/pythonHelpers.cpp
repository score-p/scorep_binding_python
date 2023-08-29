#include "pythonHelpers.hpp"
#include "compat.hpp"
#include "pathUtils.hpp"
#include "pythoncapi_compat.h"

#include <stdlib.h>

namespace scorepy
{
std::string_view get_module_name(PyFrameObject& frame)
{
    PyObject* globals = PyFrame_GetGlobals(&frame);
    PyObject* module_name = PyDict_GetItemString(globals, "__name__");
    Py_DECREF(globals);
    if (module_name)
        return compat::get_string_as_utf_8(module_name);

    // this is a NUMPY special situation, see NEP-18, and Score-P issue #63
    // TODO: Use string_view/C-String to avoid creating 2 std::strings
    PyCodeObject* code = PyFrame_GetCode(&frame);
    std::string_view filename = compat::get_string_as_utf_8(code->co_filename);
    Py_DECREF(code);
    if ((filename.size() > 0) && (filename == "<__array_function__ internals>"))
        return std::string_view("numpy.__array_function__");
    else
        return std::string_view("unkown");
}

std::string get_file_name(PyFrameObject& frame)
{
    PyCodeObject* code = PyFrame_GetCode(&frame);
    PyObject* filename = code->co_filename;
    Py_DECREF(code);
    if (filename == Py_None)
    {
        return "None";
    }
    const std::string full_file_name = abspath(compat::get_string_as_utf_8(filename));
    return !full_file_name.empty() ? full_file_name : "ErrorPath";
}
} // namespace scorepy
