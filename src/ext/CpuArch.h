/* CpuArch.h  -- Detect 32bit architecture
 * Based on CpuArch.h -- CPU specific code
 * 2017-06-30 : Igor Pavlov : Public domain
 */

#ifndef __CPU_ARCH_H
#define __CPU_ARCH_H

#include "7zTypes.h"

EXTERN_C_BEGIN

#if  defined(_M_X64) \
  || defined(_M_AMD64) \
  || defined(__x86_64__) \
  || defined(__AMD64__) \
  || defined(__amd64__)
  #define MY_CPU_AMD64
  #define MY_CPU_64BIT
#endif


#if  defined(_M_IX86) \
  || defined(__i386__)
  #define MY_CPU_X86
  #define MY_CPU_32BIT
#endif


#if  defined(_M_ARM64) \
  || defined(__AARCH64EL__) \
  || defined(__AARCH64EB__) \
  || defined(__aarch64__)
  #define MY_CPU_ARM64
  #define MY_CPU_64BIT
#endif


#if  defined(_M_ARM) \
  || defined(_M_ARM_NT) \
  || defined(_M_ARMT) \
  || defined(__arm__) \
  || defined(__thumb__) \
  || defined(__ARMEL__) \
  || defined(__ARMEB__) \
  || defined(__THUMBEL__) \
  || defined(__THUMBEB__)
  #define MY_CPU_ARM
  #define MY_CPU_32BIT
#endif


#if  defined(_M_IA64) \
  || defined(__ia64__)
  #define MY_CPU_IA64
  #define MY_CPU_64BIT
#endif


#if  defined(__mips64) \
  || defined(__mips64__) \
  || (defined(__mips) && (__mips == 64 || __mips == 4 || __mips == 3))
  #define MY_CPU_64BIT
#elif defined(__mips__)
  /* #define MY_CPU_32BIT */
#endif


#if  defined(__ppc64__) \
  || defined(__powerpc64__)
  #define MY_CPU_64BIT
#elif defined(__ppc__) \
  || defined(__powerpc__)
  #define MY_CPU_32BIT
#endif


#if  defined(__sparc64__)
  #define MY_CPU_64BIT
#elif defined(__sparc__)
  /* #define MY_CPU_32BIT */
#endif

EXTERN_C_END

#endif
