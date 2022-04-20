#pragma once

#include <array>
#include <functional>
#include <iostream>
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

#if PY_MAJOR_VERSION >= 3
        const char* string;
        string = PyUnicode_AsUTF8AndSize(py_string, &size);
#else
        char* string;
        PyString_AsStringAndSize(py_string, &string, &size);
#endif
        return std::string_view(string, size);
    }

    using PyCodeObject = PyCodeObject;

    using destructor = destructor;
    using code_dealloc = std::add_pointer<void(PyCodeObject*)>::type; // void(*)(PyCodeObject*)

    /**
     * @brief For CPython we need to make sure, that the we register our own dealloc function, so we
     * can handle the deleteion of code_objects in our code.
     */
    struct RegisterCodeDealloc
    {
        RegisterCodeDealloc(std::function<void(PyCodeObject* co)> on_dealloc_fun)
        {
            external_on_dealloc_fun = on_dealloc_fun;
            // PyPy does not need this, as CodeObjects are compiled, and therefore live for the
            // programms lifetime
#ifndef PYPY_VERSION
            if (!python_code_dealloc)
            {
                python_code_dealloc =
                    reinterpret_cast<compat::code_dealloc>(PyCode_Type.tp_dealloc);
                PyCode_Type.tp_dealloc = reinterpret_cast<compat::destructor>(dealloc_fun);
            }
            else
            {
                std::cerr << "WARNING: Score-P Python's code_dealloc is alredy registerd!"
                          << std::endl;
            }
#endif
        }

        static void dealloc_fun(PyCodeObject* co)
        {
            if (external_on_dealloc_fun && python_code_dealloc)
            {
                external_on_dealloc_fun(co);
                python_code_dealloc(co);
            }
        }

        inline static compat::code_dealloc python_code_dealloc;
        inline static std::function<void(PyCodeObject* co)> external_on_dealloc_fun;
    };

} // namespace compat
} // namespace scorepy
