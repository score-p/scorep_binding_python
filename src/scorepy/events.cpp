#include <algorithm>
#include <array>
#include <iostream>
#include <unordered_map>

#include <scorep/SCOREP_User_Functions.h>
#include <scorep/SCOREP_User_Variables.h>

#include <Python.h>
#include <frameobject.h>

#include "events.hpp"
#include "pythonHelpers.hpp"

namespace scorepy
{

struct region_handle
{
    constexpr region_handle() = default;
    ~region_handle() = default;
    constexpr bool operator==(const region_handle& other)
    {
        return this->value == other.value;
    }
    SCOREP_User_RegionHandle value = SCOREP_USER_INVALID_REGION;
};

constexpr region_handle uninitialised_region_handle = region_handle();

static std::unordered_map<std::uintptr_t, region_handle> regions;
static std::unordered_map<std::string, region_handle> user_regions;
static std::unordered_map<std::string, region_handle> rewind_regions;

/// Region names that are known to have no region enter event and should not report an error
/// on region exit
static const std::array<std::string, 2> EXIT_REGION_WHITELIST = {
#if PY_MAJOR_VERSION >= 3
    "threading:_bootstrap_inner", "threading:_bootstrap"
#else
    "threading:__bootstrap_inner", "threading:__bootstrap"
#endif
};

// pre c++20 hack ... c++20 knows concepts and require
template <typename T>
class has_co_firstlineno
{
    typedef char one;
    struct two
    {
        char x[2];
    };

    template <typename C>
    static one test(decltype(&C::co_firstlineno));
    template <typename C>
    static two test(...);

public:
    enum
    {
        value = sizeof(test<T>(0)) == sizeof(char)
    };
};

// c++11 -.-
template <bool B, class T = void>
using enable_if_t = typename std::enable_if<B, T>::type;

template <typename T>
enable_if_t<!has_co_firstlineno<T>::value, int> co_firstlineno(const T&)
{
    return 0;
}

template <typename T>
enable_if_t<has_co_firstlineno<T>::value, int> co_firstlineno(const T& t)
{
    return t.co_firstlineno;
}

template void scorepy::region_begin<PyFrameObject, PyCodeObject>(const PyFrameObject&);
template void scorepy::region_end<PyFrameObject, PyCodeObject>(const PyFrameObject&);

// Used for regions, that have an identifier, aka a code object id.
template <typename ScorePyFrameObject, typename ScorePyCodeObject>
void region_begin(const ScorePyFrameObject& frame)
{
    const ScorePyCodeObject& code = *frame.f_code;
    auto& region_handle = regions[reinterpret_cast<std::uintptr_t>(&code)];

    if (region_handle == uninitialised_region_handle)
    {
        std::string function_name(PyUnicode_AsUTF8(code.co_name));
        std::string module_name(get_module_name(frame));

        if (function_name != "_unsetprofile" && std::string(module_name, 0, 6) != "scorep")
        {
            int line_number = co_firstlineno(code);
            std::string file_name = get_file_name(frame);
            auto& region_name = make_region_name(module_name, function_name);
            SCOREP_User_RegionInit(&region_handle.value, NULL, NULL, region_name.c_str(),
                                   SCOREP_USER_REGION_TYPE_FUNCTION, file_name.c_str(),
                                   line_number);

            SCOREP_User_RegionSetGroup(region_handle.value,
                                       std::string(module_name, 0, module_name.find('.')).c_str());
        }
        else
        {
            return;
        }
    }
    SCOREP_User_RegionEnter(region_handle.value);
}

// Used for regions, that have an identifier, aka a code object id. (instrumenter regions and
// some decorated regions)
void region_begin(const std::string& function_name, const std::string& module,
                  const std::string& file_name, const std::uint64_t line_number,
                  const std::uintptr_t& identifier)
{
    auto& region_handle = regions[identifier];

    if (region_handle == uninitialised_region_handle)
    {
        auto& region_name = make_region_name(module, function_name);
        SCOREP_User_RegionInit(&region_handle.value, NULL, NULL, region_name.c_str(),
                               SCOREP_USER_REGION_TYPE_FUNCTION, file_name.c_str(), line_number);

        SCOREP_User_RegionSetGroup(region_handle.value,
                                   std::string(module, 0, module.find('.')).c_str());
    }
    SCOREP_User_RegionEnter(region_handle.value);
}

// Used for regions, that only have a function name, a module, a file and a line number (user
// regions)
void region_begin(const std::string& function_name, const std::string& module,
                  const std::string& file_name, const std::uint64_t line_number)
{
    const auto& region_name = make_region_name(module, function_name);
    auto& region_handle = user_regions[region_name];

    if (region_handle == uninitialised_region_handle)
    {
        SCOREP_User_RegionInit(&region_handle.value, NULL, NULL, region_name.c_str(),
                               SCOREP_USER_REGION_TYPE_FUNCTION, file_name.c_str(), line_number);

        SCOREP_User_RegionSetGroup(region_handle.value,
                                   std::string(module, 0, module.find('.')).c_str());
    }
    SCOREP_User_RegionEnter(region_handle.value);
}

template <typename ScorePyFrameObject, typename ScorePyCodeObject>
void region_end(const ScorePyFrameObject& frame)
{
    const ScorePyCodeObject& code = *frame.f_code;
    const auto it_region = regions.find(reinterpret_cast<std::uintptr_t>(&code));
    if (it_region != regions.end())
    {
        SCOREP_User_RegionEnd(it_region->second.value);
    }
    else
    {
        std::string function_name(PyUnicode_AsUTF8(code.co_name));
        std::string module_name = get_module_name(frame);
        if (function_name != "_unsetprofile" && std::string(module_name, 0, 6) != "scorep")
        {
            auto& region_name = make_region_name(module_name, function_name);
            region_end_error_handling(region_name);
        }
        else
        {
            return;
        }
    }
}

// Used for regions, that have an identifier, aka a code object id. (instrumenter regions and
// some decorated regions)
void region_end(const std::string& function_name, const std::string& module,
                const std::uintptr_t& identifier)
{
    const auto it_region = regions.find(identifier);
    if (it_region != regions.end())
    {
        SCOREP_User_RegionEnd(it_region->second.value);
    }
    else
    {
        auto& region_name = make_region_name(module, function_name);
        region_end_error_handling(region_name);
    }
}

// Used for regions, that only have a function name, a module (user regions)
void region_end(const std::string& function_name, const std::string& module)
{
    auto& region_name = make_region_name(module, function_name);
    const auto it_region = user_regions.find(region_name);
    if (it_region != user_regions.end())
    {
        SCOREP_User_RegionEnd(it_region->second.value);
    }
    else
    {
        region_end_error_handling(region_name);
    }
}

void region_end_error_handling(const std::string& region_name)
{
    static region_handle error_region;
    static SCOREP_User_ParameterHandle scorep_param = SCOREP_USER_INVALID_PARAMETER;
    static bool error_printed = false;

    if (std::find(EXIT_REGION_WHITELIST.begin(), EXIT_REGION_WHITELIST.end(), region_name) !=
        EXIT_REGION_WHITELIST.end())
    {
        return;
    }

    if (error_region.value == SCOREP_USER_INVALID_REGION)
    {
        SCOREP_User_RegionInit(&error_region.value, NULL, NULL, "error_region",
                               SCOREP_USER_REGION_TYPE_FUNCTION, "scorep.cpp", 0);
        SCOREP_User_RegionSetGroup(error_region.value, "error");
    }
    SCOREP_User_RegionEnter(error_region.value);
    SCOREP_User_ParameterString(&scorep_param, "leave-region", region_name.c_str());
    SCOREP_User_RegionEnd(error_region.value);

    if (!error_printed)
    {
        std::cerr << "SCOREP_BINDING_PYTHON ERROR: There was a region exit without an enter!\n"
                  << "SCOREP_BINDING_PYTHON ERROR: For details look for \"error_region\" in "
                     "the trace or profile."
                  << std::endl;
        error_printed = true;
    }
}

void rewind_begin(std::string region_name, std::string file_name, std::uint64_t line_number)
{
    auto pair = rewind_regions.emplace(make_pair(region_name, region_handle()));
    bool inserted_new = pair.second;
    auto& handle = pair.first->second;
    if (inserted_new)
    {
        SCOREP_User_RegionInit(&handle.value, NULL, NULL, region_name.c_str(),
                               SCOREP_USER_REGION_TYPE_FUNCTION, file_name.c_str(), line_number);
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

} // namespace scorepy
