#include "classes.hpp"
#include "methods.hpp"
#include <Python.h>

#if PY_VERSION_HEX < 0x03000000
PyMODINIT_FUNC init_bindings(void)
{
    (void)Py_InitModule("_bindings", scorepy::getMethodTable());
}
#else  /*python 3*/
static struct PyModuleDef scorepmodule = { PyModuleDef_HEAD_INIT, "_bindings", /* name of module */
                                           NULL, /* module documentation, may be NULL */
                                           -1,   /* size of per-interpreter state of the module,
                                                    or -1 if the module keeps state in global
                                                    variables. */
                                           scorepy::getMethodTable() };
PyMODINIT_FUNC PyInit__bindings(void)
{
    auto* ctracerType = &scorepy::getCInstrumenterType();
    if (PyType_Ready(ctracerType) < 0)
        return nullptr;

    auto* m = PyModule_Create(&scorepmodule);
    if (!m)
    {
        return nullptr;
    }

    Py_INCREF(ctracerType);
    if (PyModule_AddObject(m, "CInstrumenter", (PyObject*)ctracerType) < 0)
    {
        Py_DECREF(ctracerType);
        Py_DECREF(m);
        return nullptr;
    }

    return m;
}
#endif /*python 3*/
