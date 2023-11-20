#include "pythonHelpers.hpp"
#include "compat.hpp"
#include "pathUtils.hpp"
#include "pythoncapi_compat.h"

#include <sstream>
#include <stdlib.h>

namespace scorepy
{
std::string get_module_name(PyFrameObject& frame)
{
    const char* self_name = nullptr;
    PyObject* locals = PyFrame_GetLocals(&frame);
    PyObject* self = PyDict_GetItemString(locals, "self");
    if (self)
    {
        Py_INCREF(self);
        PyTypeObject* type = Py_TYPE(self);
        self_name = _PyType_Name(type);
        Py_DECREF(self);
    }
    Py_DECREF(locals);

    PyObject* globals = PyFrame_GetGlobals(&frame);
    PyObject* module_name = PyDict_GetItemString(globals, "__name__");
    Py_DECREF(globals);
    if (module_name)
    {
        std::stringstream result;
        result << compat::get_string_as_utf_8(module_name);
        if (self_name)
            result << '.' << self_name;
        return std::move(result).str();
    }

    // this is a NUMPY special situation, see NEP-18, and Score-P issue #63
    // TODO: Use string_view/C-String to avoid creating 2 std::strings
    PyCodeObject* code = PyFrame_GetCode(&frame);
    std::string_view filename = compat::get_string_as_utf_8(code->co_filename);
    Py_DECREF(code);
    if ((filename.size() > 0) && (filename == "<__array_function__ internals>"))
        return std::move(std::string("numpy.__array_function__"));
    else
        return std::move(std::string("unkown"));
}

std::string get_file_name(PyFrameObject& frame)
{
    PyCodeObject* code = PyFrame_GetCode(&frame);
    PyObject* filename = code->co_filename;
    Py_DECREF(code);
    if (filename == Py_None)
    {
        return std::move(std::string("None"));
    }
    const auto full_file_name = abspath(compat::get_string_as_utf_8(filename));
    return !full_file_name.empty() ? std::move(full_file_name) : "ErrorPath";
}
} // namespace scorepy
