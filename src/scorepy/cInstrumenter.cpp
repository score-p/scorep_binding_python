#include "cInstrumenter.hpp"
#include "events.hpp"
#include "pythonHelpers.hpp"
#include <algorithm>
#include <array>
#include <string>

namespace scorepy
{
static const std::string& make_region_name(const char* moduleName, const char* name)
{
    static std::string region;
    region = moduleName;
    region += ":";
    region += name;
    return region;
}

void CInstrumenter::enable_instrumenter()
{
    const auto callback = [](PyObject* obj, PyFrameObject* frame, int what, PyObject* arg) -> int {
        return fromPyObject(obj)->onEvent(*frame, what, arg) ? 0 : -1;
    };
    if (tracingOrProfiling)
    {
        PyEval_SetTrace(callback, toPyObject());
    }
    else
    {
        PyEval_SetProfile(callback, toPyObject());
    }
}

void CInstrumenter::disable_instrumenter()
{
    if (tracingOrProfiling)
        PyEval_SetTrace(nullptr, nullptr);
    else
        PyEval_SetProfile(nullptr, nullptr);
}

/// Mapping of PyTrace_* to it's string representations
/// List taken from CPythons sysmodule.c
static const std::array<std::string, 8> whatStrings = { "call",     "exception", "line",
                                                        "return",   "c_call",    "c_exception",
                                                        "c_return", "opcode" };

// Required because:  `sys.getprofile()` returns the user object (2nd arg to PyEval_SetTrace)
// So `sys.setprofile(sys.getprofile())` will not round-trip as it will try to call the
// 2nd arg through pythons dispatch function. Hence make the object callable.
// See https://nedbatchelder.com/text/trace-function.html for details
PyObject* CInstrumenter::operator()(PyFrameObject& frame, const char* what, PyObject* arg)
{
    const auto itWhat = std::find(whatStrings.begin(), whatStrings.end(), what);
    const int iWhat = itWhat == whatStrings.end() ? -1 : std::distance(whatStrings.begin(), itWhat);
    // To speed up further event processing install this class directly as the handler
    // But we might be inside a `sys.settrace` call where the user wanted to set another function
    // which would then be overwritten here. Hence use the CALL event which avoids the problem
    if (iWhat == PyTrace_CALL)
        enable_instrumenter();
    if (onEvent(frame, iWhat, arg))
    {
        Py_INCREF(toPyObject());
        return toPyObject();
    }
    else
        return nullptr;
}

bool CInstrumenter::onEvent(PyFrameObject& frame, int what, PyObject*)
{
    switch (what)
    {
    case PyTrace_CALL:
    {
        const PyCodeObject& code = *frame.f_code;
        const char* name = PyUnicode_AsUTF8(code.co_name);
        const char* moduleName = get_module_name(frame);
        assert(name);
        assert(moduleName);
        // TODO: Use string_view/CString comparison?
        if (std::string(name) != "_unsetprofile" && std::string(moduleName, 0, 6) != "scorep")
        {
            const int lineNumber = code.co_firstlineno;
            const auto& regionName = make_region_name(moduleName, name);
            const auto fileName = get_file_name(frame);
            region_begin(regionName, moduleName, fileName, lineNumber);
        }
        break;
    }
    case PyTrace_RETURN:
    {
        const PyCodeObject& code = *frame.f_code;
        const char* name = PyUnicode_AsUTF8(code.co_name);
        const char* moduleName = get_module_name(frame);
        assert(name);
        assert(moduleName);
        // TODO: Use string_view/CString comparison?
        if (std::string(name) != "_unsetprofile" && std::string(moduleName, 0, 6) != "scorep")
        {
            const auto& regionName = make_region_name(moduleName, name);
            region_end(regionName);
        }
        break;
    }
    }
    return true;
}

} // namespace scorepy
