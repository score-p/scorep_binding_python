#pragma once

#include <Python.h>
#include <frameobject.h>
#include <string>
#include <type_traits>

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

namespace detail
{
    template <typename TFunc>
    struct ReplaceArgsToPyObject;

    template <typename TFunc>
    using ReplaceArgsToPyObject_t = typename ReplaceArgsToPyObject<TFunc>::type;
} // namespace detail

/// Cast a function pointer to a python-bindings compatible function pointer
/// Replaces all Foo* by PyObject* for all types Foo that are PyObject compatible
template <typename TFunc>
auto cast_to_PyFunc(TFunc* func) -> detail::ReplaceArgsToPyObject_t<TFunc>*
{
    return reinterpret_cast<detail::ReplaceArgsToPyObject_t<TFunc>*>(func);
}

/// Return the module name the frame belongs to.
/// The pointer is valid for the lifetime of the frame
std::string_view get_module_name(const PyFrameObject& frame);
/// Return the file name the frame belongs to
std::string get_file_name(const PyFrameObject& frame);

// Implementation details
namespace detail
{

    template <typename>
    struct make_void
    {
        typedef void type;
    };
    template <typename T>
    using void_t = typename make_void<T>::type;

    template <class T, class = void>
    struct IsPyObject : std::false_type
    {
    };
    template <class T>
    struct IsPyObject<T*> : IsPyObject<T>
    {
    };

    template <class T>
    struct IsPyObject<T, void_t<decltype(std::declval<T>().to_PyObject())>> : std::true_type
    {
    };

    template <typename TResult, typename... TArgs>
    struct ReplaceArgsToPyObject<TResult(TArgs...)>
    {
        template <typename T>
        using replace = typename std::conditional<IsPyObject<T>::value, PyObject*, T>::type;
        using type = TResult(replace<TArgs>...);
    };
} // namespace detail
} // namespace scorepy
