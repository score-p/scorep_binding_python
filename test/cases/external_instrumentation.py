import scorep.user

import instrumentation2

instrumentation2.bar = scorep.user.region()(instrumentation2.bar)
