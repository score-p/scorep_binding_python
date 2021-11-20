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
        {
            return nullptr;
        }
        scorepy::PyRefObject empty_dict(PyDict_New(), scorepy::adopt_object);
        if (!empty_dict)
        {
            return nullptr;
        }
        return PyBaseObject_Type.tp_new(type, empty_tuple, empty_dict);
    }

    static void CInstrumenter_dealloc(scorepy::CInstrumenter* self)
    {
        self->deinit();
        Py_TYPE(self)->tp_free(self->to_PyObject());
    }

    static int CInstrumenter_init(scorepy::CInstrumenter* self, PyObject* args, PyObject* kwds)
    {
        static const char* kwlist[] = { "interface", nullptr };
        const char* interface_cstring;

        if (!PyArg_ParseTupleAndKeywords(args, kwds, "s", const_cast<char**>(kwlist),
                                         &interface_cstring))
        {
            return -1;
        }

        const std::string interface_string = interface_cstring;
        scorepy::InstrumenterInterface interface;
        if (interface_string == "Trace")
        {
            interface = scorepy::InstrumenterInterface::Trace;
        }
        else if (interface_string == "Profile")
        {
            interface = scorepy::InstrumenterInterface::Profile;
        }
        else
        {
            PyErr_Format(PyExc_TypeError, "Expected 'Trace' or 'Profile', got '%s'",
                         interface_cstring);
            return -1;
        }

        self->init(interface);
        return 0;
    }

    static PyObject* CInstrumenter_get_interface(scorepy::CInstrumenter* self, void*)
    {
        const char* result =
            self->interface == scorepy::InstrumenterInterface::Trace ? "Trace" : "Profile";
        return PyUnicode_FromString(result);
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

        if (!PyArg_ParseTupleAndKeywords(args, kwds, "OsO", const_cast<char**>(kwlist), &frame,
                                         &event, &arg))
        {
            return nullptr;
        }
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
        { "interface", scorepy::cast_to_PyFunc(CInstrumenter_get_interface), nullptr,
          "Return the used interface for instrumentation", nullptr },
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
    type.tp_dealloc = scorepy::cast_to_PyFunc(CInstrumenter_dealloc);
    type.tp_methods = methods;
    type.tp_call = scorepy::cast_to_PyFunc(CInstrumenter_call);
    type.tp_getset = getseters;
    type.tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE;
    type.tp_doc = "Class for the C instrumenter interface of Score-P";
    return type;
}

} // namespace scorepy
