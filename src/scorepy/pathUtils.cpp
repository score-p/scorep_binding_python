#include "pathUtils.hpp"
#include <cerrno>
#include <limits>
#include <unistd.h>

namespace scorepy
{
static std::string getcwd()
{
    std::string result;
    const char* cwd;
    constexpr size_t chunk_size = 512;
    do
    {
        const size_t new_size = result.size() + chunk_size;
        if (new_size > std::numeric_limits<int>::max())
        {
            cwd = nullptr;
            break;
        }
        result.resize(new_size);
        cwd = ::getcwd(&result.front(), result.size());
    } while (!cwd && errno == ERANGE);
    if (cwd)
        result.resize(result.find('\0', result.size() - chunk_size));
    else
        result.clear();
    return result;
}

void normalize_path(std::string& path)
{
    // 2 slashes are kept, 1 or more than 2 become 1 according to POSIX
    const size_t num_slashes = (path.find_first_not_of('/') == 2) ? 2 : 1;
    const size_t path_len = path.size();
    size_t cur_out = num_slashes;
    for (size_t i = cur_out; i != path_len + 1; ++i)
    {
        if (i == path_len || path[i] == '/')
        {
            const char prior = path[cur_out - 1];
            if (prior == '/') // Double slash -> ignore
                continue;
            if (prior == '.')
            {
                const char second_prior = path[cur_out - 2];
                if (second_prior == '/') // '/./'
                {
                    --cur_out;
                    continue;
                }
                else if (second_prior == '.' && path[cur_out - 3] == '/') // '/../'
                {
                    if (cur_out < 3 + num_slashes) // already behind root slash
                        cur_out -= 2;
                    else
                    {
                        const auto prior_slash = path.rfind('/', cur_out - 4);
                        cur_out = prior_slash + 1;
                    }
                    continue;
                }
            }
            if (i == path_len)
                break;
        }
        path[cur_out++] = path[i];
    }
    // Remove trailing slash
    if (cur_out > num_slashes && path[cur_out - 1] == '/')
        --cur_out;
    path.resize(cur_out);
}

std::string abspath(std::string_view input_path)
{
    std::string result;
    if (input_path[0] != '/')
    {
        result = getcwd();
        // On error exit
        if (result.empty())
            return result;
        // Prepend CWD
        result.append(1, '/').append(input_path);
    }
    else
    {
        result = input_path;
    }
    normalize_path(result);
    return result;
}
} // namespace scorepy
