#include <stdint.h>

typedef  void (*pFunction)(void);

void main() {
    uint32_t jump_address = *(uint32_t*) (0x8000000 + 4);
    pFunction JumpToApp = (pFunction) jump_address;
    JumpToApp();
}