// Offline host-side tests: g++ -std=c++17 -Wall -Wextra -pedantic test_hk_sequencer.cpp -o /tmp/test_hk && /tmp/test_hk
#include "HKSequencer.h"
#include <cassert>
using namespace xgo_hk_diag;
int main() {
  Sequencer s;
  assert(s.update(0,false)==0);
  assert(s.update(100,true)==0); // start countdown
  assert(s.running() && s.phase()==0);
  assert(s.update(2099,false)==0);
  assert(s.update(2100,false)==kHKMask);
  assert(s.update(3099,false)==kHKMask);
  assert(s.update(3100,false)==0);
  assert(s.update(4100,false)==kHKMask); // phase1 100ms
  assert(s.phase()==1);
  assert(s.update(4200,false)==0);
  assert(s.update(4700,false)==kHKMask);
  // Check every transition with a 1ms tick, including end and retrigger behavior.
  for (uint32_t t=4701;t<30000;++t) s.update(t,false);
  assert(!s.running());
  assert(s.update(30000,false)==0);
  assert(s.update(30001,true)==0);
  assert(s.running());
  assert(s.update(32001,false)==kHKMask);
  s.reset();
  assert(!s.running());
  // One large forward jump should drain completed phases without infinite loop.
  s.update(100,true);
  assert(s.update(30000,false)==0);
  assert(!s.running());
}
