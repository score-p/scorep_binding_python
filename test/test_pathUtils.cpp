#include "scorepy/pathUtils.hpp"
#include <iostream>
#include <stdexcept>

#define TEST(condition)                                                                            \
    if (!(condition))                                                                              \
    throw std::runtime_error(std::string("Test ") + #condition + " failed at " + __FILE__ + ":" +  \
                             std::to_string(__LINE__))

int main()
{
    using scorepy::abspath;
    // Multiple slashes at start collapsed to 1
    TEST(abspath("/abc") == "/abc");
    TEST(abspath("//abc") == "//abc");
    TEST(abspath("///abc") == "/abc");
    TEST(abspath("////abc") == "/abc");
    // Trailing slashes and multiple slashes removed
    TEST(abspath("/abc/") == "/abc");
    TEST(abspath("/abc//") == "/abc");
    TEST(abspath("/abc//de") == "/abc/de");
    TEST(abspath("/abc//de///fg") == "/abc/de/fg");
    TEST(abspath("/abc//de///fg/") == "/abc/de/fg");
    TEST(abspath("/abc//de///fg////") == "/abc/de/fg");
    TEST(abspath("//abc/") == "//abc");
    TEST(abspath("//abc//") == "//abc");
    TEST(abspath("//abc//de") == "//abc/de");
    TEST(abspath("//abc//de///fg") == "//abc/de/fg");
    TEST(abspath("//abc//de///fg/") == "//abc/de/fg");
    TEST(abspath("//abc//de///fg////") == "//abc/de/fg");
    // Single dots removed
    TEST(abspath("/./abc/./defgh/./ijkl/.") == "/abc/defgh/ijkl");
    TEST(abspath("/./abc././def.gh/./ijkl././.mn/.") == "/abc./def.gh/ijkl./.mn");
    // Going up 1 level removes prior folder
    TEST(abspath("/abc/..") == "/");
    TEST(abspath("//abc/..") == "//");
    TEST(abspath("///abc/..") == "/");
    TEST(abspath("/abc/../de") == "/de");
    TEST(abspath("//abc/../de") == "//de");
    TEST(abspath("///abc/../de") == "/de");
    TEST(abspath("/abc/de/../fg") == "/abc/fg");
    TEST(abspath("/abc/de/../../fg") == "/fg");
    TEST(abspath("/abc/de../../fg") == "/abc/fg");
    TEST(abspath("/abc../de/../fg") == "/abc../fg");
    // Going up from root does nothing
    TEST(abspath("/../ab") == "/ab");
    TEST(abspath("//../ab") == "//ab");
    TEST(abspath("///../ab") == "/ab");
    TEST(abspath("/abc/defgh/../../ijkl") == "/ijkl");
    TEST(abspath("//abc/defgh/../../ijkl") == "//ijkl");
    TEST(abspath("///abc/defgh/../../ijkl") == "/ijkl");
}
