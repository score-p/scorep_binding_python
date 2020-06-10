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
        return from_PyObject(obj)->on_event(*frame, what, arg) ? 0 : -1;
    };
    if (interface == InstrumenterInterface::Trace)
        PyEval_SetTrace(callback, to_PyObject());
    else
        PyEval_SetProfile(callback, to_PyObject());
}

void CInstrumenter::disable_instrumenter()
{
    if (interface == InstrumenterInterface::Trace)
        PyEval_SetTrace(nullptr, nullptr);
    else
        PyEval_SetProfile(nullptr, nullptr);
}

/// Mapping of PyTrace_* to it's string representations
/// List taken from CPythons sysmodule.c
static const std::array<std::string, 8> WHAT_STRINGS = { "call",     "exception", "line",
                                                         "return",   "c_call",    "c_exception",
                                                         "c_return", "opcode" };

// Required because:  `sys.getprofile()` returns the user object (2nd arg to PyEval_SetTrace)
// So `sys.setprofile(sys.getprofile())` will not round-trip as it will try to call the
// 2nd arg through pythons dispatch function. Hence make the object callable.
// See https://nedbatchelder.com/text/trace-function.html for details
PyObject* CInstrumenter::operator()(PyFrameObject& frame, const char* what_string, PyObject* arg)
{
    const auto it_what = std::find(WHAT_STRINGS.begin(), WHAT_STRINGS.end(), what_string);
    const int what =
        it_what == WHAT_STRINGS.end() ? -1 : std::distance(WHAT_STRINGS.begin(), it_what);
    // To speed up further event processing install this class directly as the handler
    // But we might be inside a `sys.settrace` call where the user wanted to set another function
    // which would then be overwritten here. Hence use the CALL event which avoids the problem
    if (what == PyTrace_CALL)
        enable_instrumenter();
    if (on_event(frame, what, arg))
    {
        Py_INCREF(to_PyObject());
        return to_PyObject();
    }
    else
        return nullptr;
}

bool CInstrumenter::on_event(PyFrameObject& frame, int what, PyObject*)
{
    switch (what)
    {
    case PyTrace_CALL:
    {
        const PyCodeObject& code = *frame.f_code;
        const char* name = PyUnicode_AsUTF8(code.co_name);
        const char* module_name = get_module_name(frame);
        assert(name);
        assert(module_name);
        // TODO: Use string_view/CString comparison?
        if (std::string(name) != "_unsetprofile" && std::string(module_name, 0, 6) != "scorep")
        {
            const int line_number = code.co_firstlineno;
            const auto& region_name = make_region_name(module_name, name);
            const auto file_name = get_file_name(frame);
            region_begin(region_name, module_name, file_name, line_number);
        }
        break;
    }
    case PyTrace_RETURN:
    {
        const PyCodeObject& code = *frame.f_code;
        const char* name = PyUnicode_AsUTF8(code.co_name);
        const char* module_name = get_module_name(frame);
        assert(name);
        assert(module_name);
        // TODO: Use string_view/CString comparison?
        if (std::string(name) != "_unsetprofile" && std::string(module_name, 0, 6) != "scorep")
        {
            const auto& region_name = make_region_name(module_name, name);
            region_end(region_name);
        }
        break;
    }
    }
    return true;
}

} // namespace scorepy
