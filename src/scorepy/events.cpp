#include <algorithm>
#include <array>

#include <Python.h>

#include "compat.hpp"
#include "events.hpp"
#include "pythonHelpers.hpp"

namespace scorepy
{

std::unordered_map<compat::PyCodeObject*, region_handle> regions;
static std::unordered_map<std::string, region_handle> user_regions;
static std::unordered_map<std::string, region_handle> rewind_regions;

/**
 * @brief when Python PyCodeObject is deallocated, remove it from our regions list.
 *
 * @param co code object to remove
 */
void on_dealloc(PyCodeObject* co)
{
    regions.erase(co);
}

static compat::RegisterCodeDealloc register_dealloc(on_dealloc);

// Used for regions, that have an identifier, aka a code object id. (instrumenter regions and
// some decorated regions)
void region_begin(std::string_view& function_name, std::string_view& module,
                  const std::string& file_name, const std::uint64_t line_number,
                  compat::PyCodeObject* identifier)
{
    region_handle& region = regions[identifier];

    if (region == uninitialised_region_handle)
    {
        auto& region_name = make_region_name(module, function_name);
        SCOREP_User_RegionInit(&region.value, NULL, NULL, region_name.c_str(),
                               SCOREP_USER_REGION_TYPE_FUNCTION, file_name.c_str(), line_number);

        SCOREP_User_RegionSetGroup(region.value, std::string(module, 0, module.find('.')).c_str());
    }
    SCOREP_User_RegionEnter(region.value);
}

// Used for regions, that only have a function name, a module, a file and a line number (user
// regions)
void region_begin(std::string_view& function_name, std::string_view& module,
                  const std::string& file_name, const std::uint64_t line_number)
{
    std::string region_name = make_region_name(module, function_name);
    region_handle& region = user_regions[region_name];

    if (region == uninitialised_region_handle)
    {
        SCOREP_User_RegionInit(&region.value, NULL, NULL, region_name.c_str(),
                               SCOREP_USER_REGION_TYPE_FUNCTION, file_name.c_str(), line_number);

        SCOREP_User_RegionSetGroup(region.value, std::string(module, 0, module.find('.')).c_str());
    }
    SCOREP_User_RegionEnter(region.value);
}

// Used for regions, that have an identifier, aka a code object id. (instrumenter regions and
// some decorated regions)
void region_end(std::string_view& function_name, std::string_view& module,
                compat::PyCodeObject* identifier)
{
    const auto it_region = regions.find(identifier);
    if (it_region != regions.end())
    {
        SCOREP_User_RegionEnd(it_region->second.value);
    }
    else
    {
        std::string region_name = make_region_name(module, function_name);
        region_end_error_handling(region_name);
    }
}

// Used for regions, that only have a function name, a module (user regions)
void region_end(std::string_view& function_name, std::string_view& module)
{
    std::string region_name = make_region_name(module, function_name);
    auto it_region = user_regions.find(region_name);
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

    if (std::find(compat::exit_region_whitelist.begin(), compat::exit_region_whitelist.end(),
                  region_name) != compat::exit_region_whitelist.end())
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
