/*
 * scorep.c
 *
 *  Created on: 09.05.2017
 *      Author: gocht
 */

#include <Python.h>
#include <scorep/SCOREP_User.h>

static PyObject *enable_recording(PyObject *self, PyObject *args)
{
    SCOREP_RECORDING_ON();
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *disable_recording(PyObject *self, PyObject *args)
{
    SCOREP_RECORDING_OFF();
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *region_enter(PyObject *self, PyObject *args)
{
    const char *region;

    if (!PyArg_ParseTuple(args, "s", &region))
        return NULL;

    SCOREP_USER_REGION_BY_NAME_BEGIN(region, SCOREP_USER_REGION_TYPE_FUNCTION)

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *region_exit(PyObject *self, PyObject *args)
{
    const char *region;

    if (!PyArg_ParseTuple(args, "s", &region))
        return NULL;

    SCOREP_USER_REGION_BY_NAME_END(region)

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef ScorePMethods[] = {
    {"region_enter", region_enter, METH_VARARGS, "enter a region."},
    {"region_exit", region_exit, METH_VARARGS, "exit a region."},
    {"enable_recording", enable_recording, METH_VARARGS, "disable scorep recording."},
    {"disable_recording", disable_recording, METH_VARARGS, "disable scorep recording."},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static struct PyModuleDef scorepmodule = {PyModuleDef_HEAD_INIT,
    "scorep", /* name of module */
    NULL,     /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    ScorePMethods};

PyMODINIT_FUNC PyInit_scorep(void)
{
    return PyModule_Create(&scorepmodule);
}
