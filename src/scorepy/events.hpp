#pragma once
#include <Python.h>

#include <cstdint>
#include <string>

namespace scorepy
{
/// Combine the arguments into a region name
/// Return value is a statically allocated string to avoid memory (re)allocations
inline const std::string& make_region_name(const std::string& module_name, const std::string& name)
{
    static std::string region;
    region = module_name;
    region += ":";
    region += name;
    return region;
}

template <typename PythonFrameObject, typename PythonCodeObject>
void region_begin(const PythonFrameObject& frame);

void region_begin(const std::string& function_name, const std::string& module,
                  const std::string& file_name, const std::uint64_t line_number,
                  const std::uintptr_t& identifier);
void region_begin(const std::string& function_name, const std::string& module,
                  const std::string& file_name, const std::uint64_t line_number);

template <typename PythonFrameObject, typename PythonCodeObject>
void region_end(const PythonFrameObject& frame);

void region_end(const std::string& function_name, const std::string& module,
                const std::uintptr_t& identifier);
void region_end(const std::string& function_name, const std::string& module);

void region_end_error_handling(const std::string& region_name);

void rewind_begin(std::string region_name, std::string file_name, std::uint64_t line_number);
void rewind_end(std::string region_name, bool value);

void parameter_int(std::string name, int64_t value);
void parameter_uint(std::string name, uint64_t value);
void parameter_string(std::string name, std::string value);
} // namespace scorepy

#if PY_MAJOR_VERSION >= 3
#include <frameobject.h>
extern template void scorepy::region_begin<PyFrameObject, PyCodeObject>(const PyFrameObject&);
extern template void scorepy::region_end<PyFrameObject, PyCodeObject>(const PyFrameObject&);
#endif
