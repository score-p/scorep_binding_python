#include "events.hpp"
#include <iostream>
#include <scorep/SCOREP_User_Functions.h>
#include <scorep/SCOREP_User_Variables.h>
#include <unordered_map>

namespace scorepy
{

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
        SCOREP_User_RegionSetGroup(handle.value, std::string(module, 0, module.find('.')).c_str());
    }
    SCOREP_User_RegionEnter(handle.value);
}

void region_end(const std::string& region_name)
{
    const auto itRegion = regions.find(region_name);
    if (itRegion != regions.end())
    {
        SCOREP_User_RegionEnd(itRegion->second.value);
    }
    else
    {
        static region_handle error_region;
        static SCOREP_User_ParameterHandle scorep_param = SCOREP_USER_INVALID_PARAMETER;
        static bool error_printed = false;

        if (error_region.value == SCOREP_USER_INVALID_REGION)
        {
            SCOREP_User_RegionInit(&error_region.value, NULL, &SCOREP_User_LastFileHandle,
                                   "error_region", SCOREP_USER_REGION_TYPE_FUNCTION, "scorep.cpp",
                                   0);
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

} // namespace scorepy
