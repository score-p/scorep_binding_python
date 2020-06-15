#pragma once

#include <Python.h>

namespace scorepy
{
/// Return the type info to define for the python module
PyTypeObject& getCInstrumenterType();
} // namespace scorepy
