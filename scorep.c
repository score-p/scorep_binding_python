
/*
 * Copyright 2017, Technische Universitaet Dresden, Germany, all rights reserved.
 * Author: Andreas Gocht
 *
 * Permission to use, copy, modify, and distribute this Python software and
 * its associated documentation for any purpose without fee is hereby
 * granted, provided that the above copyright notice appears in all copies,
 * and that both that copyright notice and this permission notice appear in
 * supporting documentation, and that the name of TU Dresden is not used in
 * advertising or publicity pertaining to distribution of the software
 * without specific, written prior permission.
 */

#include <Python.h>
#include <scorep/SCOREP_User.h>

extern const char* SCOREP_GetExperimentDirName(void);

static PyObject* enable_recording(PyObject* self, PyObject* args)
{
    SCOREP_RECORDING_ON();
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* disable_recording(PyObject* self, PyObject* args)
{
    SCOREP_RECORDING_OFF();
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* region_begin(PyObject* self, PyObject* args)
{
    const char* region;

    if (!PyArg_ParseTuple(args, "s", &region))
        return NULL;

    SCOREP_USER_REGION_BY_NAME_BEGIN(region, SCOREP_USER_REGION_TYPE_FUNCTION)

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* region_end(PyObject* self, PyObject* args)
{
    const char* region;

    if (!PyArg_ParseTuple(args, "s", &region))
        return NULL;

    SCOREP_USER_REGION_BY_NAME_END(region)

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* parameter_string(PyObject* self, PyObject* args)
{
    const char* name;
    const char* value;

    if (!PyArg_ParseTuple(args, "ss", &name, &value))
        return NULL;

    SCOREP_USER_PARAMETER_STRING(name, value)

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* parameter_int(PyObject* self, PyObject* args)
{
    const char* name;
    long long value;

    if (!PyArg_ParseTuple(args, "sL", &name, &value))
        return NULL;

    SCOREP_USER_PARAMETER_INT64(name, value)

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* parameter_uint(PyObject* self, PyObject* args)
{
    const char* name;
    unsigned long long value;

    if (!PyArg_ParseTuple(args, "sK", &name, &value))
        return NULL;

    SCOREP_USER_PARAMETER_UINT64(name, value)

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* get_expiriment_dir_name(PyObject* self, PyObject* args)
{

    return PyUnicode_FromString(SCOREP_GetExperimentDirName());
}

static PyMethodDef ScorePMethods[] = {
    { "region_begin", region_begin, METH_VARARGS, "enter a region." },
    { "region_end", region_end, METH_VARARGS, "exit a region." },
    { "enable_recording", enable_recording, METH_VARARGS, "disable scorep recording." },
    { "disable_recording", disable_recording, METH_VARARGS, "disable scorep recording." },
    { "parameter_int", parameter_int, METH_VARARGS, "User parameter int." },
    { "parameter_uint", parameter_uint, METH_VARARGS, "User parameter uint." },
    { "parameter_string", parameter_string, METH_VARARGS, "User parameter string." },
    { "get_expiriment_dir_name", get_expiriment_dir_name, METH_VARARGS,
      "Get the Score-P experiment dir." },
    { NULL, NULL, 0, NULL } /* Sentinel */
};

#if PY_VERSION_HEX < 0x03000000
#ifndef USE_MPI
PyMODINIT_FUNC initscorep(void)
{
    (void)Py_InitModule("scorep", ScorePMethods);
}
#else
PyMODINIT_FUNC initscorep_mpi(void)
{
    (void)Py_InitModule("scorep_mpi", ScorePMethods);
}
#endif
#else
static struct PyModuleDef scorepmodule = { PyModuleDef_HEAD_INIT, "scorep", /* name of module */
                                           NULL, /* module documentation, may be NULL */
                                           -1,   /* size of per-interpreter state of the module,
                                                    or -1 if the module keeps state in global
                                                    variables. */
                                           ScorePMethods };
#ifndef USE_MPI
PyMODINIT_FUNC PyInit_scorep(void)
{
    return PyModule_Create(&scorepmodule);
}
#else
PyMODINIT_FUNC PyInit_scorep_mpi(void)
{
    return PyModule_Create(&scorepmodule);
}
#endif
#endif
