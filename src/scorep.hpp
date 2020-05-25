#pragma once

#include <Python.h>

namespace scorepy
{
/// Return the methods to define for the python module
PyMethodDef* getMethodTable();
} // namespace scorepy
