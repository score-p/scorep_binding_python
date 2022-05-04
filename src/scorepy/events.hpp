#pragma once
#include <cstdint>
#include <string>
#include <unordered_map>

#include <scorep/SCOREP_User_Functions.h>
#include <scorep/SCOREP_User_Variables.h>

#include "compat.hpp"

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
    constexpr bool operator!=(const region_handle& other)
    {
        return this->value != other.value;
    }

    SCOREP_User_RegionHandle value = SCOREP_USER_INVALID_REGION;
};

struct caller_handle
{
    constexpr caller_handle() = default;
    ~caller_handle() = default;
    constexpr bool operator==(const caller_handle& other)
    {
        return this->value == other.value;
    }
    constexpr bool operator!=(const caller_handle& other)
    {
        return this->value != other.value;
    }

    SCOREP_User_ParameterHandle value = SCOREP_USER_INVALID_PARAMETER;
};

constexpr region_handle uninitialised_region_handle = region_handle();
constexpr caller_handle uninitialised_caller_handle = caller_handle();

/// Combine the arguments into a region name
inline std::string make_region_name(std::string_view& module_name, std::string_view& name)
{
    std::string region;
    region = module_name;
    region += ":";
    region += name;
    return region;
}

extern std::unordered_map<compat::PyCodeObject*, region_handle> regions;
extern std::unordered_map<compat::PyCodeObject*, caller_handle> callers;

/** tries to enter a region. Return true on success
 *
 */
inline bool try_region_begin(compat::PyCodeObject* identifier)
{
    auto it = regions.find(identifier);
    if (it != regions.end())
    {
        SCOREP_User_RegionEnter(it->second.value);
        return true;
    }
    else
    {
        return false;
    }
}

void region_begin(std::string_view& function_name, std::string_view& module,
                  const std::string& file_name, const std::uint64_t line_number,
                  compat::PyCodeObject* identifier);
void region_begin(std::string_view& function_name, std::string_view& module,
                  const std::string& file_name, const std::uint64_t line_number);

/** tries to end a region. Return true on success
 *
 */
inline bool try_region_end(compat::PyCodeObject* identifier)
{
    auto it_region = regions.find(identifier);
    if (it_region != regions.end())
    {
        SCOREP_User_RegionEnd(it_region->second.value);
        return true;
    }
    else
    {
        return false;
    }
}

void region_end(std::string_view& function_name, std::string_view& module,
                compat::PyCodeObject* identifier);
void region_end(std::string_view& function_name, std::string_view& module);

inline bool try_add_caller(compat::PyCodeObject* identifier, const std::uint64_t line_number)
{
    auto it = callers.find(identifier);
    if (it != callers.end())
    {
        SCOREP_User_ParameterInt64(&it->second.value, "", line_number);
        return true;
    }
    else
    {
        return false;
    }
}
void region_add_caller(std::string_view& function_name, std::string_view& module,
                       const std::string& file_name, const std::uint64_t line_number,
                       compat::PyCodeObject* identifier);

void region_end_error_handling(const std::string& region_name);

void rewind_begin(std::string region_name, std::string file_name, std::uint64_t line_number);
void rewind_end(std::string region_name, bool value);

void parameter_int(std::string name, int64_t value);
void parameter_uint(std::string name, uint64_t value);
void parameter_string(std::string name, std::string value);
} // namespace scorepy
