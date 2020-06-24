#pragma once

#include <Python.h>
#include <frameobject.h>

namespace scorepy
{
/// Interface to Python used to implement an instrumenter
/// See sys.settrace/setprofile
enum class InstrumenterInterface
{
    Profile,
    Trace
};

struct CInstrumenter
{
    PyObject_HEAD;
    InstrumenterInterface interface;
    PyObject* threading_module;
    PyObject* threading_set_instrumenter;

    void init(InstrumenterInterface interface);
    void deinit();
    void enable_instrumenter();
    void disable_instrumenter();

    /// Callback for when this object is called directly
    PyObject* operator()(PyFrameObject& frame, const char* what, PyObject* arg);

    /// These casts are valid as long as `PyObject_HEAD` is the first entry in this struct
    PyObject* to_PyObject()
    {
        return reinterpret_cast<PyObject*>(this);
    }
    static CInstrumenter* from_PyObject(PyObject* o)
    {
        return reinterpret_cast<CInstrumenter*>(o);
    }

private:
    /// Callback for Python trace/profile events. Return true for success
    bool on_event(PyFrameObject& frame, int what, PyObject* arg);
};

} // namespace scorepy
