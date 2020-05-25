#pragma once

#include <Python.h>
#include <frameobject.h>
#include <string>

namespace scorepy
{

struct retain_object_t
{
};
struct adopt_object_t
{
};
/// Marker to indicate that an owner is added, i.e. refCnt is increased
constexpr retain_object_t retain_object{};
/// Marker to take over ownership, not touching the refCnt
constexpr adopt_object_t adopt_object{};

/// Slim, owning wrapper over a PyObject*
/// Decays implictely to a PyObject*
class PyRefObject
{
    PyObject* o_;

public:
    explicit PyRefObject(PyObject* o, adopt_object_t) noexcept : o_(o)
    {
    }
    explicit PyRefObject(PyObject* o, retain_object_t) noexcept : o_(o)
    {
        Py_XINCREF(o_);
    }
    PyRefObject(PyRefObject&& rhs) noexcept : o_(rhs.o_)
    {
        rhs.o_ = nullptr;
    }
    PyRefObject& operator=(PyRefObject&& rhs) noexcept
    {
        o_ = rhs.o_;
        rhs.o_ = nullptr;
        return *this;
    }
    ~PyRefObject() noexcept
    {
        Py_XDECREF(o_);
    }

    operator PyObject*() const noexcept
    {
        return o_;
    }
};

/// Return the module name the frame belongs to.
/// The pointer is valid for the lifetime of the frame
const char* get_module_name(const PyFrameObject& frame);
/// Return the file name the frame belongs to
std::string get_file_name(const PyFrameObject& frame);

} // namespace scorepy
