#pragma once

#include <string>

namespace scorepy
{
/// A//B, A/./B and A/foo/../B all become A/B
/// Assumes an absolute, non-empty path
void normalize_path(std::string& path);
/// Makes the path absolute and normalized, see Python os.path.abspath
std::string abspath(std::string_view input_path);
} // namespace scorepy
