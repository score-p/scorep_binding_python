#include "cInstrumenter.hpp"
#include "events.hpp"
#include "pythonHelpers.hpp"
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
    // TODO: Known issue:  `sys.getprofile()` returns the user object (2nd arg)
    // So `sys.setprofile(sys.getprofile())` will not round-trip as it will try to call the
    // 2nd arg. If it is nullptr (here) it means it will be disabled completely
    // See https://nedbatchelder.com/text/trace-function.html for details
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
