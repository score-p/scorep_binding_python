#include <Python.h>
#include <iostream>
#include <scorep/SCOREP_User_Functions.h>
#include <scorep/SCOREP_User_Variables.h>
#include <set>
#include <string>
#include <unordered_map>

namespace scorep
{
// SCOREP_User_RegionHandle handle = SCOREP_USER_INVALID_REGION

struct region_handle
{
    region_handle() = default;
    ~region_handle() = default;
    SCOREP_User_RegionHandle value = SCOREP_USER_INVALID_REGION;
};

static std::unordered_map<std::string, region_handle> regions;
static std::unordered_map<std::string, region_handle> rewind_regions;

void region_begin(const std::string& region_name, std::string module, std::string file_name,
                  std::uint64_t line_number)
{
    auto pair = regions.emplace(make_pair(region_name, region_handle()));
    bool inserted_new = pair.second;
    auto& handle = pair.first->second;
    if (inserted_new)
    {
        SCOREP_User_RegionInit(&handle.value, NULL, &SCOREP_User_LastFileHandle,
                               region_name.c_str(), SCOREP_USER_REGION_TYPE_FUNCTION,
                               file_name.c_str(), line_number);
        SCOREP_User_RegionSetGroup(handle.value, module.c_str());
    }
    SCOREP_User_RegionEnter(handle.value);
}

void region_end(const std::string& region_name)
{
    auto& handle = regions.at(region_name);
    SCOREP_User_RegionEnd(handle.value);
}

void rewind_begin(std::string region_name, std::string file_name, std::uint64_t line_number)
{
    auto pair = rewind_regions.emplace(make_pair(region_name, region_handle()));
    bool inserted_new = pair.second;
    auto& handle = pair.first->second;
    if (inserted_new)
    {
        SCOREP_User_RegionInit(&handle.value, NULL, &SCOREP_User_LastFileHandle,
                               region_name.c_str(), SCOREP_USER_REGION_TYPE_FUNCTION,
                               file_name.c_str(), line_number);
    }
    SCOREP_User_RewindRegionEnter(handle.value);
}

void rewind_end(std::string region_name, bool value)
{
    auto& handle = rewind_regions.at(region_name);
    /* don't call SCOREP_ExitRewindRegion, as
     * SCOREP_User_RewindRegionEnd does some additional magic
     * */
    SCOREP_User_RewindRegionEnd(handle.value, value);
}

void parameter_int(std::string name, int64_t value)
{
    static SCOREP_User_ParameterHandle scorep_param = SCOREP_USER_INVALID_PARAMETER;
    SCOREP_User_ParameterInt64(&scorep_param, name.c_str(), value);
}

void parameter_uint(std::string name, uint64_t value)
{
    static SCOREP_User_ParameterHandle scorep_param = SCOREP_USER_INVALID_PARAMETER;
    SCOREP_User_ParameterUint64(&scorep_param, name.c_str(), value);
}

void parameter_string(std::string name, std::string value)
{
    static SCOREP_User_ParameterHandle scorep_param = SCOREP_USER_INVALID_PARAMETER;
    SCOREP_User_ParameterString(&scorep_param, name.c_str(), value.c_str());
}

void oa_region_begin(std::string region_name, std::string file_name, std::uint64_t line_number)
{
    auto& handle = regions[region_name];
    SCOREP_User_OaPhaseBegin(&handle.value, &SCOREP_User_LastFileName, &SCOREP_User_LastFileHandle,
                             region_name.c_str(), SCOREP_USER_REGION_TYPE_FUNCTION,
                             file_name.c_str(), line_number);
}

void oa_region_end(std::string region_name)
{
    auto& handle = regions[region_name];
    SCOREP_User_OaPhaseEnd(handle.value);
}
} // namespace scorep

extern "C"
{

    extern const char* SCOREP_GetExperimentDirName(void);

    static PyObject* enable_recording(PyObject* self, PyObject* args)
    {
        SCOREP_User_EnableRecording();
        Py_INCREF(Py_None);
        return Py_None;
    }

    static PyObject* disable_recording(PyObject* self, PyObject* args)
    {

        SCOREP_User_DisableRecording();
        Py_INCREF(Py_None);
        return Py_None;
    }

    /** This code is not thread save. However, this does not matter as the python GIL is not
     * released.
     */
    static PyObject* region_begin(PyObject* self, PyObject* args)
    {
        const char* module;
        const char* region_name;
        const char* file_name;
        std::uint64_t line_number = 0;

        if (!PyArg_ParseTuple(args, "sssK", &module, &region_name, &file_name, &line_number))
            return NULL;

        static std::string region = "";
        region = module;
        region += ":";
        region += region_name;
        scorep::region_begin(region, module, file_name, line_number);

        Py_INCREF(Py_None);
        return Py_None;
    }

    /** This code is not thread save. However, this does not matter as the python GIL is not
     * released.
     */
    static PyObject* region_end(PyObject* self, PyObject* args)
    {
        const char* module;
        const char* region_name;

        if (!PyArg_ParseTuple(args, "ss", &module, &region_name))
            return NULL;

        static std::string region = "";
        region = module;
        region += ":";
        region += region_name;
        scorep::region_end(region);

        Py_INCREF(Py_None);
        return Py_None;
    }

    static PyObject* rewind_begin(PyObject* self, PyObject* args)
    {
        const char* region_name;
        const char* file_name;
        std::uint64_t line_number = 0;

        if (!PyArg_ParseTuple(args, "ssK", &region_name, &file_name, &line_number))
            return NULL;

        scorep::rewind_begin(region_name, file_name, line_number);

        Py_INCREF(Py_None);
        return Py_None;
    }

    static PyObject* rewind_end(PyObject* self, PyObject* args)
    {
        const char* region_name;
        PyObject* value; // false C-Style

        if (!PyArg_ParseTuple(args, "sO", &region_name, &value))
            return NULL;

        // TODO cover PyObject_IsTrue(value) == -1 (error case)
        scorep::rewind_end(region_name, PyObject_IsTrue(value) == 1);

        Py_INCREF(Py_None);
        return Py_None;
    }

    static PyObject* oa_region_begin(PyObject* self, PyObject* args)
    {
        const char* region;
        const char* file_name;
        std::uint64_t line_number = 0;

        if (!PyArg_ParseTuple(args, "ssK", &region, &file_name, &line_number))
            return NULL;

        scorep::oa_region_begin(region, file_name, line_number);

        Py_INCREF(Py_None);
        return Py_None;
    }

    static PyObject* oa_region_end(PyObject* self, PyObject* args)
    {
        const char* region;

        if (!PyArg_ParseTuple(args, "s", &region))
            return NULL;

        scorep::oa_region_end(region);

        Py_INCREF(Py_None);
        return Py_None;
    }

    static PyObject* parameter_string(PyObject* self, PyObject* args)
    {
        const char* name;
        const char* value;

        if (!PyArg_ParseTuple(args, "ss", &name, &value))
            return NULL;

        scorep::parameter_string(name, value);

        Py_INCREF(Py_None);
        return Py_None;
    }

    static PyObject* parameter_int(PyObject* self, PyObject* args)
    {
        const char* name;
        long long value;

        if (!PyArg_ParseTuple(args, "sL", &name, &value))
            return NULL;

        scorep::parameter_int(name, value);

        Py_INCREF(Py_None);
        return Py_None;
    }

    static PyObject* parameter_uint(PyObject* self, PyObject* args)
    {
        const char* name;
        unsigned long long value;

        if (!PyArg_ParseTuple(args, "sK", &name, &value))
            return NULL;

        scorep::parameter_uint(name, value);

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
        { "rewind_begin", rewind_begin, METH_VARARGS, "rewind begin." },
        { "rewind_end", rewind_end, METH_VARARGS, "rewind end." },
        { "oa_region_begin", oa_region_begin, METH_VARARGS, "enter an online access region." },
        { "oa_region_end", oa_region_end, METH_VARARGS, "exit an online access region." },
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
    PyMODINIT_FUNC initscorep_bindings(void)
    {
        (void)Py_InitModule("scorep_bindings", ScorePMethods);
    }
#else  /*python 3*/
    static struct PyModuleDef scorepmodule = { PyModuleDef_HEAD_INIT,
                                               "scorep_bindings", /* name of module */
                                               NULL, /* module documentation, may be NULL */
                                               -1,   /* size of per-interpreter state of the module,
                                                        or -1 if the module keeps state in global
                                                        variables. */
                                               ScorePMethods };
    PyMODINIT_FUNC PyInit_scorep_bindings(void)
    {
        return PyModule_Create(&scorepmodule);
    }
#endif /*python 3*/
}
