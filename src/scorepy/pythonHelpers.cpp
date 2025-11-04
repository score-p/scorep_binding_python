#include "pythonHelpers.hpp"
#include "compat.hpp"
#include "pathUtils.hpp"
#include "pythoncapi_compat.h"

#include <cstdio>
#include <sstream>
#include <stdlib.h>
#include <string>

namespace scorepy
{

static PyObject* get_self_from_frame(PyFrameObject* frame)
{
    PyObject* self = nullptr;

#if PY_VERSION_HEX >= 0x030C0000 // Python 3.12+
    // Added in 3.12: directly fetch a local variable by name.
    self = PyFrame_GetVarString(frame, "self");
    if (!self && PyErr_Occurred())
        PyErr_Clear();
#else
    PyObject* locals = PyFrame_GetLocals(frame); // New reference
    if (locals)
    {
        PyObject* tmp = PyDict_GetItemString(locals, "self"); // Borrowed
        if (tmp)
        {
            Py_INCREF(tmp);
            self = tmp;
        }
        Py_DECREF(locals);
    }
#endif
    return self;
}

std::string get_module_name(PyFrameObject& frame)
{
    const char* self_name = nullptr;

    PyObject* self = get_self_from_frame(&frame);
    if (self)
    {
        PyTypeObject* type = Py_TYPE(self);
        self_name = _PyType_Name(type);
        Py_DECREF(self);
    }

    // --- get module name from globals ---------------------------------------
    PyObject* globals = PyFrame_GetGlobals(&frame);                             // New reference
    PyObject* module_name = globals ? PyDict_GetItemString(globals, "__name__") // Borrowed
                                      :
                                      nullptr;
    if (globals)
        Py_DECREF(globals);

    if (module_name)
    {
        std::stringstream result;
        // compat::get_string_as_utf_8() is assumed to convert PyObject* → UTF-8 std::string
        result << compat::get_string_as_utf_8(module_name);
        if (self_name)
            result << '.' << self_name;
        return result.str();
    }

    // --- special-case NumPy internal frames ---------------------------------
    PyCodeObject* code = PyFrame_GetCode(&frame);
    std::string_view filename = compat::get_string_as_utf_8(code->co_filename);
    Py_DECREF(code);

    if (filename == "<__array_function__ internals>")
        return "numpy.__array_function__";

    return "unknown";
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
