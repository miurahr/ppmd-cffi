//
// Created by miurahr on 2021/04/07.
// Based on 7zTypes.h - 2017-07-17 : Igor Pavlov : Public domain
//

#ifndef PPMD_CFFI_PPMDARCH_H
#define PPMD_CFFI_PPMDARCH_H

#include <stddef.h>

#ifndef EXTERN_C_BEGIN
#ifdef __cplusplus
#define EXTERN_C_BEGIN extern "C" {
#define EXTERN_C_END }
#else
#define EXTERN_C_BEGIN
#define EXTERN_C_END
#endif
#endif

EXTERN_C_BEGIN

typedef unsigned char Byte;
typedef short Int16;
typedef unsigned short UInt16;
typedef int Int32;
typedef unsigned int UInt32;

#if defined(_MSC_VER) || defined(__BORLANDC__)
typedef __int64 Int64;
typedef unsigned __int64 UInt64;
#define UINT64_CONST(n) n
#else
typedef long long int Int64;
typedef unsigned long long int UInt64;
#define UINT64_CONST(n) n ## ULL
#endif


typedef int Bool;
#define True 1
#define False 0


/* The following interfaces use first parameter as pointer to structure */

typedef struct IByteIn IByteIn;
struct IByteIn
{
    Byte (*Read)(const IByteIn *p); /* reads one byte, returns 0 in case of EOF or error */
};
#define IByteIn_Read(p) (p)->Read(p)


typedef struct IByteOut IByteOut;
struct IByteOut
{
    void (*Write)(const IByteOut *p, Byte b);
};
#define IByteOut_Write(p, b) (p)->Write(p, b)


typedef struct ISzAlloc ISzAlloc;
typedef const ISzAlloc * ISzAllocPtr;

struct ISzAlloc
{
    void *(*Alloc)(size_t size);
    void (*Free)(void *address); /* address can be NULL */
};

#define ISzAlloc_Alloc(p, size) (p)->Alloc(size)
#define ISzAlloc_Free(p, a) (p)->Free(a)

#if  defined(_M_IX86) \
  || defined(__i386__) \
  || defined(_M_ARM) \
  || defined(_M_ARM_NT) \
  || defined(_M_ARMT) \
  || defined(__arm__) \
  || defined(__thumb__) \
  || defined(__ARMEL__) \
  || defined(__ARMEB__) \
  || defined(__THUMBEL__) \
  || defined(__THUMBEB__) \
  || defined(__mips__) \
  || defined(__ppc__) \
  || defined(__powerpc__) \
  || defined(__sparc__)
  #define PPMD_32BIT
#endif

EXTERN_C_END

#endif //PPMD_CFFI_PPMDARCH_H
