#include "pythonHelpers.hpp"
#include "pathUtils.hpp"
#include <stdlib.h>

namespace scorepy
{
CString get_module_name(const PyFrameObject& frame)
{
    PyObject* module_name = PyDict_GetItemString(frame.f_globals, "__name__");
    if (module_name)
        return get_string_from_python(*module_name);

    // this is a NUMPY special situation, see NEP-18, and Score-P issue #63
    const CString filename = get_string_from_python(*frame.f_code->co_filename);
    if (filename == "<__array_function__ internals>")
    {
        return "numpy.__array_function__";
    }
    else
    {
        return "unkown";
    }
}

CString get_file_name(const PyFrameObject& frame)
{
    PyObject* filename = frame.f_code->co_filename;
    if (filename == Py_None)
    {
        return "None";
    }
    const std::string full_file_name = abspath(PyUnicode_AsUTF8(filename));
    return !full_file_name.empty() ? CStrubg(full_file_name) : CString("ErrorPath");
}
} // namespace scorepy
