#!/bin/sh

gcc -Wp,-MMD,linux-6.3.5/arch/x86/tools/.relocs_32.o.d -Wall -Wmissing-prototypes -Wstrict-prototypes -O2 -fomit-frame-pointer -std=gnu11 -Wdeclaration-after-statement   -I./linux-6.3.5/tools/include  -c -o linux-6.3.5/arch/x86/tools/relocs_32.o linux-6.3.5/arch/x86/tools/relocs_32.c
gcc -Wp,-MMD,linux-6.3.5/arch/x86/tools/.relocs_64.o.d -Wall -Wmissing-prototypes -Wstrict-prototypes -O2 -fomit-frame-pointer -std=gnu11 -Wdeclaration-after-statement   -I./linux-6.3.5/tools/include  -c -o linux-6.3.5/arch/x86/tools/relocs_64.o linux-6.3.5/arch/x86/tools/relocs_64.c
gcc -Wp,-MMD,linux-6.3.5/arch/x86/tools/.relocs_common.o.d -Wall -Wmissing-prototypes -Wstrict-prototypes -O2 -fomit-frame-pointer -std=gnu11 -Wdeclaration-after-statement   -I./linux-6.3.5/tools/include  -c -o linux-6.3.5/arch/x86/tools/relocs_common.o linux-6.3.5/arch/x86/tools/relocs_common.c
gcc -O2 -o linux-6.3.5/arch/x86/tools/relocs linux-6.3.5/arch/x86/tools/relocs_32.o linux-6.3.5/arch/x86/tools/relocs_64.o linux-6.3.5/arch/x86/tools/relocs_common.o 
echo "ziopera"
# gcc -g -gdwarf-4 -Wp,-MMD -Wall -Wmissing-prototypes -Wstrict-prototypes -O2 -fomit-frame-pointer -std=gnu11 -Wdeclaration-after-statement  -I/home/nicola/relocs-chall/linux-6.3.5/tools/include  -o gen_elf /home/nicola/relocs-chall/linux-6.3.5/arch/x86/tools/gen_elf.c
