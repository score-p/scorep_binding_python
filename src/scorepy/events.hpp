#pragma once

#include <Python.h>
#include <cstdint>
#include <string>

namespace scorepy
{
void region_begin(const PyObject*&, const std::string& region_name, std::string module,
                  std::string file_name, std::uint64_t line_number);
void region_end(const PyObject*&);

void rewind_begin(std::string region_name, std::string file_name, std::uint64_t line_number);
void rewind_end(std::string region_name, bool value);

void parameter_int(std::string name, int64_t value);
void parameter_uint(std::string name, uint64_t value);
void parameter_string(std::string name, std::string value);

void oa_region_begin(std::string region_name, std::string file_name, std::uint64_t line_number);
void oa_region_end(std::string region_name);
} // namespace scorepy
