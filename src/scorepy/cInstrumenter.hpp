#pragma once

#include <Python.h>
#include <frameobject.h>

namespace scorepy
{
struct CInstrumenter
{
    PyObject_HEAD;
    bool tracingOrProfiling;

    void init(bool tracingOrProfiling)
    {
        this->tracingOrProfiling = tracingOrProfiling;
    }
    void enable_instrumenter();
    void disable_instrumenter();

    /// These casts are valid as long as `PyObject_HEAD` is the first entry in this struct
    PyObject* toPyObject()
    {
        return reinterpret_cast<PyObject*>(this);
    }
    static CInstrumenter* fromPyObject(PyObject* o)
    {
        return reinterpret_cast<CInstrumenter*>(o);
    }

private:
    /// Callback for Python trace/profile events. Return true for success
    bool onEvent(PyFrameObject& frame, int what, PyObject* arg);
};

} // namespace scorepy
