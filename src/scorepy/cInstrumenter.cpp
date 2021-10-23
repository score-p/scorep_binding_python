#include "cInstrumenter.hpp"
#include "events.hpp"
#include "pythonHelpers.hpp"
#include <algorithm>
#include <array>
#include <cstdint>
#include <string>

namespace scorepy
{

void CInstrumenter::init(InstrumenterInterface interface)
{
    this->interface = interface;
    threading_module = PyImport_ImportModule("threading");
    if (threading_module)
    {
        const char* name = (interface == InstrumenterInterface::Trace) ? "settrace" : "setprofile";
        threading_set_instrumenter = PyObject_GetAttrString(threading_module, name);
    }
}

void CInstrumenter::deinit()
{
    Py_CLEAR(threading_module);
    Py_CLEAR(threading_set_instrumenter);
}

void CInstrumenter::enable_instrumenter()
{
    const auto callback = [](PyObject* obj, PyFrameObject* frame, int what, PyObject* arg) -> int
    { return from_PyObject(obj)->on_event(*frame, what, arg) ? 0 : -1; };
    if (threading_set_instrumenter)
    {
        PyRefObject result(PyObject_CallFunction(threading_set_instrumenter, "O", to_PyObject()),
                           adopt_object);
    }
    if (interface == InstrumenterInterface::Trace)
    {
        PyEval_SetTrace(callback, to_PyObject());
    }
    else
    {
        PyEval_SetProfile(callback, to_PyObject());
    }
}

void CInstrumenter::disable_instrumenter()
{
    if (interface == InstrumenterInterface::Trace)
    {
        PyEval_SetTrace(nullptr, nullptr);
    }
    else
    {
        PyEval_SetProfile(nullptr, nullptr);
    }
    if (threading_set_instrumenter)
    {
        PyRefObject result(PyObject_CallFunction(threading_set_instrumenter, "O", Py_None),
                           adopt_object);
    }
}

/// Mapping of PyTrace_* to it's string representations
/// List taken from CPythons sysmodule.c
static const std::array<std::string, 8> WHAT_STRINGS = { "call",     "exception", "line",
                                                         "return",   "c_call",    "c_exception",
                                                         "c_return", "opcode" };

template <typename TCollection, typename TElement>
int index_of(TCollection&& col, const TElement& element)
{
    const auto it = std::find(col.cbegin(), col.cend(), element);
    if (it == col.end())
    {
        return -1;
    }
    else
    {
        return std::distance(col.begin(), it);
    }
}

// Required because:  `sys.getprofile()` returns the user object (2nd arg to PyEval_SetTrace)
// So `sys.setprofile(sys.getprofile())` will not round-trip as it will try to call the
// 2nd arg through pythons dispatch function. Hence make the object callable.
// See https://nedbatchelder.com/text/trace-function.html for details
PyObject* CInstrumenter::operator()(PyFrameObject& frame, const char* what_string, PyObject* arg)
{
    const int what = index_of(WHAT_STRINGS, what_string);
    // To speed up further event processing install this class directly as the handler
    // But we might be inside a `sys.settrace` call where the user wanted to set another function
    // which would then be overwritten here. Hence use the CALL event which avoids the problem
    if (what == PyTrace_CALL)
    {
        enable_instrumenter();
    }
    if (on_event(frame, what, arg))
    {
        Py_INCREF(to_PyObject());
        return to_PyObject();
    }
    else
    {
        return nullptr;
    }
}

bool CInstrumenter::on_event(PyFrameObject& frame, int what, PyObject*)
{
    switch (what)
    {
    case PyTrace_CALL:
    {
        const PyCodeObject& code = *frame.f_code;
        region_begin(frame, code);
        break;
    }
    case PyTrace_RETURN:
    {
        const PyCodeObject& code = *frame.f_code;
        region_end(frame, code);
        break;
    }
    }
    return true;
}

} // namespace scorepy
