#pragma once

#include <array>
#include <string_view>

#include <Python.h>
#include <frameobject.h>

namespace scorepy
{
namespace compat
{
    /// Region names that are known to have no region enter event and should not report an error
    /// on region exit
    static const std::array<std::string, 2> exit_region_whitelist = {
#if PY_MAJOR_VERSION >= 3
        "threading:_bootstrap_inner", "threading:_bootstrap"
#else
        "threading:__bootstrap_inner", "threading:__bootstrap"
#endif
    };

    inline std::string_view get_string_as_utf_8(PyObject* py_string)
    {
        Py_ssize_t size = 0;
        const char* string;

#if PY_MAJOR_VERSION >= 3
        string = PyUnicode_AsUTF8AndSize(py_string, &size);
#else
        PyObject* tmp_string = PyUnicode_AsUTF8String(py_string);
        size = PyUnicode_GET_DATA_SIZE(tmp_string);
        string = PyUnicode_AS_DATA(tmp_string);
#endif
        return std::string_view(string, size);
    }

    using PyCodeObject = PyCodeObject;

} // namespace compat
} // namespace scorepy
