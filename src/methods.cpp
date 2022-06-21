#include "methods.hpp"
#include "scorepy/events.hpp"
#include "scorepy/pathUtils.hpp"
#include <Python.h>
#include <cstdint>
#include <scorep/SCOREP_User_Functions.h>

#include <iostream>

extern "C"
{

    extern const char* SCOREP_GetExperimentDirName(void);

    extern void SCOREP_RegisterExitHandler(void);
    extern void SCOREP_FinalizeMeasurement(void);

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

    static PyObject* try_region_begin(PyObject* self, PyObject* args)
    {
        PyObject* identifier = nullptr;
        if (!PyArg_ParseTuple(args, "O", &identifier))
        {
            return NULL;
        }

        bool success = scorepy::try_region_begin(reinterpret_cast<PyCodeObject*>(identifier));
        if (success)
        {
            Py_RETURN_TRUE;
        }
        else
        {
            Py_RETURN_FALSE;
        }
    }

    /** This code is not thread save. However, this does not matter as the python GIL is not
     * released.
     */
    static PyObject* region_begin(PyObject* self, PyObject* args)
    {
        const char* module_cstr;
        const char* function_name_cstr;
        const char* file_name_cstr;
        Py_ssize_t module_len;
        Py_ssize_t function_name_len;
        Py_ssize_t file_name_len;

        PyObject* identifier = nullptr;
        std::uint64_t line_number = 0;

        if (!PyArg_ParseTuple(args, "s#s#s#KO", &module_cstr, &module_len, &function_name_cstr,
                              &function_name_len, &file_name_cstr, &file_name_len, &line_number,
                              &identifier))
        {
            return NULL;
        }

        std::string_view module(module_cstr, module_len);
        std::string_view function_name(function_name_cstr, function_name_len);
        std::string_view file_name(file_name_cstr, file_name_len);

        std::string file_name_abs = scorepy::abspath(file_name);

        if (identifier == nullptr or identifier == Py_None)
        {
            scorepy::region_begin(function_name, module, file_name_abs, line_number);
        }
        else
        {
            scorepy::region_begin(function_name, module, file_name_abs, line_number,
                                  reinterpret_cast<PyCodeObject*>(identifier));
        }

        Py_RETURN_NONE;
    }

    static PyObject* try_region_end(PyObject* self, PyObject* args)
    {
        PyObject* identifier = nullptr;
        if (!PyArg_ParseTuple(args, "O", &identifier))
        {
            return NULL;
        }

        bool success = scorepy::try_region_end(reinterpret_cast<PyCodeObject*>(identifier));
        if (success)
        {
            Py_RETURN_TRUE;
        }
        else
        {
            Py_RETURN_FALSE;
        }
    }

    /** This code is not thread save. However, this does not matter as the python GIL is not
     * released.
     */
    static PyObject* region_end(PyObject* self, PyObject* args)
    {
        const char* module_cstr;
        const char* function_name_cstr;
        Py_ssize_t module_len;
        Py_ssize_t function_name_len;
        PyObject* identifier = nullptr;

        if (!PyArg_ParseTuple(args, "s#s#O", &module_cstr, &module_len, &function_name_cstr,
                              &function_name_len, &identifier))
        {
            return NULL;
        }

        std::string_view module(module_cstr, module_len);
        std::string_view function_name(function_name_cstr, function_name_len);

        if (identifier == nullptr or identifier == Py_None)
        {
            scorepy::region_end(function_name, module);
        }
        else
        {
            scorepy::region_end(function_name, module, reinterpret_cast<PyCodeObject*>(identifier));
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

    static PyObject* abspath(PyObject* self, PyObject* args)
    {
        const char* path;

        if (!PyArg_ParseTuple(args, "s", &path))
            return NULL;

        return PyUnicode_FromString(scorepy::abspath(path).c_str());
    }

    static PyObject* force_finalize(PyObject* self, PyObject* args)
    {
        SCOREP_FinalizeMeasurement();
        Py_RETURN_NONE;
    }

    static PyObject* reregister_exit_handler(PyObject* self, PyObject* args)
    {
        SCOREP_RegisterExitHandler();
        Py_RETURN_NONE;
    }

    static PyMethodDef ScorePMethods[] = {
        { "region_begin", region_begin, METH_VARARGS, "enter a region." },
        { "try_region_begin", try_region_begin, METH_VARARGS,
          "Tries to begin a region, returns True on Sucess." },
        { "region_end", region_end, METH_VARARGS, "exit a region." },
        { "try_region_end", try_region_end, METH_VARARGS,
          "Tries to end a region, returns True on Sucess." },
        { "rewind_begin", rewind_begin, METH_VARARGS, "rewind begin." },
        { "rewind_end", rewind_end, METH_VARARGS, "rewind end." },
        { "enable_recording", enable_recording, METH_VARARGS, "disable scorep recording." },
        { "disable_recording", disable_recording, METH_VARARGS, "disable scorep recording." },
        { "parameter_int", parameter_int, METH_VARARGS, "User parameter int." },
        { "parameter_uint", parameter_uint, METH_VARARGS, "User parameter uint." },
        { "parameter_string", parameter_string, METH_VARARGS, "User parameter string." },
        { "get_experiment_dir_name", get_experiment_dir_name, METH_VARARGS,
          "Get the Score-P experiment dir." },
        { "abspath", abspath, METH_VARARGS, "Estimates the absolute Path." },
        { "force_finalize", force_finalize, METH_VARARGS, "triggers a finalize" },
        { "reregister_exit_handler", reregister_exit_handler, METH_VARARGS,
          "register an new atexit handler" },
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
