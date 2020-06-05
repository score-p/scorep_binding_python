#include "methods.hpp"
#include <Python.h>

#if PY_VERSION_HEX < 0x03000000
PyMODINIT_FUNC initscorep_bindings(void)
{
    (void)Py_InitModule("scorep_bindings", scorepy::getMethodTable());
}
#else  /*python 3*/
static struct PyModuleDef scorepmodule = { PyModuleDef_HEAD_INIT,
                                           "scorep_bindings", /* name of module */
                                           NULL, /* module documentation, may be NULL */
                                           -1,   /* size of per-interpreter state of the module,
                                                    or -1 if the module keeps state in global
                                                    variables. */
                                           scorepy::getMethodTable() };
PyMODINIT_FUNC PyInit_scorep_bindings(void)
{
    return PyModule_Create(&scorepmodule);
}
#endif /*python 3*/
