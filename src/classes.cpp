#include "classes.hpp"
#include "scorepy/cInstrumenter.hpp"
#include "scorepy/pythonHelpers.hpp"
#include <Python.h>
#include <type_traits>

static_assert(std::is_trivial<scorepy::CInstrumenter>::value,
              "Must be trivial or object creation by Python is UB");
static_assert(std::is_standard_layout<scorepy::CInstrumenter>::value,
              "Must be standard layout or object creation by Python is UB");

extern "C"
{

    /// tp_new implementation that calls object.__new__ with not args to allow ABC classes to work
    static PyObject* call_object_new(PyTypeObject* type, PyObject*, PyObject*)
    {
        scorepy::PyRefObject empty_tuple(PyTuple_New(0), scorepy::adopt_object);
        if (!empty_tuple)
            return nullptr;
        scorepy::PyRefObject empty_dict(PyDict_New(), scorepy::adopt_object);
        if (!empty_dict)
            return nullptr;
        return PyBaseObject_Type.tp_new(type, empty_tuple, empty_dict);
    }

    static int CInstrumenter_init(scorepy::CInstrumenter* self, PyObject* args, PyObject* kwds)
    {
        static const char* kwlist[] = { "tracing_or_profiling", nullptr };
        int tracing_or_profiling;

        if (!PyArg_ParseTupleAndKeywords(args, kwds, "p", const_cast<char**>(kwlist),
                                         &tracing_or_profiling))
            return -1;

        self->init(tracing_or_profiling != 0);
        return 0;
    }

    static PyObject* CInstrumenter_get_tracingOrProfiling(scorepy::CInstrumenter* self, void*)
    {
        scorepy::PyRefObject result(self->tracing_or_profiling ? Py_True : Py_False,
                                    scorepy::retain_object);
        return result;
    }

    static PyObject* CInstrumenter_enable_instrumenter(scorepy::CInstrumenter* self, PyObject*)
    {
        self->enable_instrumenter();
        Py_RETURN_NONE;
    }

    static PyObject* CInstrumenter_disable_instrumenter(scorepy::CInstrumenter* self, PyObject*)
    {
        self->disable_instrumenter();
        Py_RETURN_NONE;
    }

    static PyObject* CInstrumenter_call(scorepy::CInstrumenter* self, PyObject* args,
                                        PyObject* kwds)
    {
        static const char* kwlist[] = { "frame", "event", "arg", nullptr };

        PyFrameObject* frame;
        const char* event;
        PyObject* arg;

        if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!sO", const_cast<char**>(kwlist),
                                         &PyFrame_Type, &frame, &event, &arg))
            return nullptr;
        return (*self)(*frame, event, arg);
    }
}

namespace scorepy
{

PyTypeObject& getCInstrumenterType()
{
    static PyMethodDef methods[] = {
        { "_enable_instrumenter", scorepy::cast_to_PyFunc(CInstrumenter_enable_instrumenter),
          METH_NOARGS, "Enable the instrumenter" },
        { "_disable_instrumenter", scorepy::cast_to_PyFunc(CInstrumenter_disable_instrumenter),
          METH_NOARGS, "Disable the instrumenter" },
        { nullptr } /* Sentinel */
    };
    static PyGetSetDef getseters[] = {
        { "tracing_or_profiling", scorepy::cast_to_PyFunc(CInstrumenter_get_tracingOrProfiling),
          nullptr, "Return whether the trace (True) or profile (False) instrumentation is used",
          nullptr },
        { nullptr } /* Sentinel */
    };
    // Sets the first few fields explicitely and remaining ones to zero
    static PyTypeObject type = {
        PyVarObject_HEAD_INIT(nullptr, 0) /* header */
        "scorep._bindings.CInstrumenter", /* tp_name */
        sizeof(CInstrumenter),            /* tp_basicsize */
    };
    type.tp_new = call_object_new;
    type.tp_init = scorepy::cast_to_PyFunc(CInstrumenter_init);
    type.tp_methods = methods;
    type.tp_call = scorepy::cast_to_PyFunc(CInstrumenter_call);
    type.tp_getset = getseters;
    type.tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE;
    type.tp_doc = "Class for the C instrumenter interface of Score-P";
    return type;
}

} // namespace scorepy
