#pragma once

#include <cassert>
#include <cstring>

namespace scorepy
{

/// Thin wrapper around a C-String (NULL-terminated sequence of chars)
class CString
{
    const char* s_;
    size_t len_;

public:
    template <size_t N>
    constexpr CString(const char (&s)[N]) : s_(s), len_(N - 1u)
    {
        static_assert(N > 0, "Cannot handle empty char array");
    }

    explicit CString(const char* s, size_t len) : s_(s), len_(len)
    {
        assert(s_);
    }

    explicit CString(const char* s) : s_(s), len_(std::strlen(s_))
    {
        assert(s_);
    }

    constexpr const char* c_str() const
    {
        return s_;
    }
    /// Find the first occurrence of the character and return a pointer to it or NULL if not found
    const char* find(char c) const
    {
        return static_cast<const char*>(std::memchr(s_, c, len_));
    }
    template <size_t N>
    bool starts_with(const char (&prefix)[N]) const
    {
        return (len_ >= N - 1u) && (std::memcmp(s_, prefix, N - 1u) == 0);
    }

    friend bool operator==(const CString& lhs, const CString& rhs)
    {
        return (lhs.len_ == rhs.len_) && (std::memcmp(lhs.s_, rhs.s_, rhs.len_) == 0);
    }
    friend bool operator!=(const CString& lhs, const CString& rhs)
    {
        return !(lhs == rhs);
    }
};

} // namespace scorepy
