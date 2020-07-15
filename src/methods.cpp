#include "methods.hpp"
#include "scorepy/events.hpp"
#include <Python.h>
#include <cstdint>
#include <scorep/SCOREP_User_Functions.h>

#include <iostream>

extern "C"
{

    extern const char* SCOREP_GetExperimentDirName(void);

    static PyObject* enable_recording(PyObject* self, PyObject* args)
    {
        SCOREP_User_EnableRecording();
        Py_RETURN_NONE;
    }

    static PyObject* disable_recording(PyObject* self, PyObject* args)
    {

        SCOREP_User_DisableRecording();
        Py_RETURN_NONE;
    }

    /** This code is not thread save. However, this does not matter as the python GIL is not
     * released.
     */
    static PyObject* region_begin(PyObject* self, PyObject* args)
    {
        const char* module;
        const char* function_name;
        const char* file_name;
        PyObject* identifier = nullptr;
        std::uint64_t line_number = 0;

        if (!PyArg_ParseTuple(args, "sssKO", &module, &function_name, &file_name, &line_number,
                              &identifier))
        {
            return NULL;
        }

        if (identifier == nullptr or identifier == Py_None)
        {
            scorepy::region_begin(function_name, module, file_name, line_number);
        }
        else
        {
            scorepy::region_begin(function_name, module, file_name, line_number,
                                  reinterpret_cast<std::uintptr_t>(identifier));
        }

        Py_RETURN_NONE;
    }

    /** This code is not thread save. However, this does not matter as the python GIL is not
     * released.
     */
    static PyObject* region_end(PyObject* self, PyObject* args)
    {
        const char* module;
        const char* function_name;
        PyObject* identifier = nullptr;

        if (!PyArg_ParseTuple(args, "ssO", &module, &function_name, &identifier))
        {
            return NULL;
        }

        if (identifier == nullptr or identifier == Py_None)
        {
            scorepy::region_end(function_name, module);
        }
        else
        {
            scorepy::region_end(function_name, module,
                                reinterpret_cast<std::uintptr_t>(identifier));
        }

        Py_RETURN_NONE;
    }

    static PyObject* rewind_begin(PyObject* self, PyObject* args)
    {
        const char* region_name;
        const char* file_name;
        std::uint64_t line_number = 0;

        if (!PyArg_ParseTuple(args, "ssK", &region_name, &file_name, &line_number))
            return NULL;

        scorepy::rewind_begin(region_name, file_name, line_number);

        Py_RETURN_NONE;
    }

    static PyObject* rewind_end(PyObject* self, PyObject* args)
    {
        const char* region_name;
        PyObject* value; // false C-Style

        if (!PyArg_ParseTuple(args, "sO", &region_name, &value))
            return NULL;

        // TODO cover PyObject_IsTrue(value) == -1 (error case)
        scorepy::rewind_end(region_name, PyObject_IsTrue(value) == 1);

        Py_RETURN_NONE;
    }

    static PyObject* oa_region_begin(PyObject* self, PyObject* args)
    {
        const char* region;
        const char* file_name;
        std::uint64_t line_number = 0;

        if (!PyArg_ParseTuple(args, "ssK", &region, &file_name, &line_number))
            return NULL;

        scorepy::oa_region_begin(region, file_name, line_number);

        Py_RETURN_NONE;
    }

    static PyObject* oa_region_end(PyObject* self, PyObject* args)
    {
        const char* region;

        if (!PyArg_ParseTuple(args, "s", &region))
            return NULL;

        scorepy::oa_region_end(region);

        Py_RETURN_NONE;
    }

    static PyObject* parameter_string(PyObject* self, PyObject* args)
    {
        const char* name;
        const char* value;

        if (!PyArg_ParseTuple(args, "ss", &name, &value))
            return NULL;

        scorepy::parameter_string(name, value);

        Py_RETURN_NONE;
    }

    static PyObject* parameter_int(PyObject* self, PyObject* args)
    {
        const char* name;
        long long value;

        if (!PyArg_ParseTuple(args, "sL", &name, &value))
            return NULL;

        scorepy::parameter_int(name, value);

        Py_RETURN_NONE;
    }

    static PyObject* parameter_uint(PyObject* self, PyObject* args)
    {
        const char* name;
        unsigned long long value;

        if (!PyArg_ParseTuple(args, "sK", &name, &value))
            return NULL;

        scorepy::parameter_uint(name, value);

        Py_RETURN_NONE;
    }

    static PyObject* get_experiment_dir_name(PyObject* self, PyObject* args)
    {

        return PyUnicode_FromString(SCOREP_GetExperimentDirName());
    }

    static PyMethodDef ScorePMethods[] = {
        { "region_begin", region_begin, METH_VARARGS, "enter a region." },
        { "region_end", region_end, METH_VARARGS, "exit a region." },
        { "rewind_begin", rewind_begin, METH_VARARGS, "rewind begin." },
        { "rewind_end", rewind_end, METH_VARARGS, "rewind end." },
        { "oa_region_begin", oa_region_begin, METH_VARARGS, "enter an online access region." },
        { "oa_region_end", oa_region_end, METH_VARARGS, "exit an online access region." },
        { "enable_recording", enable_recording, METH_VARARGS, "disable scorep recording." },
        { "disable_recording", disable_recording, METH_VARARGS, "disable scorep recording." },
        { "parameter_int", parameter_int, METH_VARARGS, "User parameter int." },
        { "parameter_uint", parameter_uint, METH_VARARGS, "User parameter uint." },
        { "parameter_string", parameter_string, METH_VARARGS, "User parameter string." },
        { "get_experiment_dir_name", get_experiment_dir_name, METH_VARARGS,
          "Get the Score-P experiment dir." },
        { NULL, NULL, 0, NULL } /* Sentinel */
    };
}

namespace scorepy
{
PyMethodDef* getMethodTable()
{
    return ScorePMethods;
}
} // namespace scorepy
