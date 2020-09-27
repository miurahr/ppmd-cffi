import cffi
import pathlib
import sys


def is_64bit() -> bool:
    return sys.maxsize > 2 ** 32


SOURCES = ['Ppmd7.c', 'Ppmd7Dec.c', 'Ppmd7Enc.c']
SRC_ROOT = pathlib.Path(__file__).parent.parent
sources = [SRC_ROOT.joinpath(s).as_posix() for s in SOURCES]

ffibuilder = cffi.FFI()

# 7zTypes.h
ffibuilder.cdef(r'''
typedef unsigned char Byte;
typedef short Int16;
typedef unsigned short UInt16;
typedef int Int32;
typedef unsigned int UInt32;
typedef long long Int64;
typedef unsigned long long UInt64;
typedef int Bool;
''')
ffibuilder.cdef(r'''
typedef struct IByteIn IByteIn;
struct IByteIn
{
  Byte (*Read)(const IByteIn *p); /* reads one byte, returns 0 in case of EOF or error */
};
typedef struct IByteOut IByteOut;
struct IByteOut
{
  void (*Write)(const IByteOut *p, Byte b);
};
''')

# Ppmd.h
ffibuilder.cdef(r'''
/* SEE-contexts for PPM-contexts with masked symbols */
typedef struct
{
  UInt16 Summ;
  Byte Shift;
  Byte Count;
  ...;
} CPpmd_See;
''')
ffibuilder.cdef(r'''
typedef struct
{
  Byte Symbol;
  Byte Freq;
  UInt16 SuccessorLow;
  UInt16 SuccessorHigh;
} CPpmd_State;
''')

if is_64bit():
    ffibuilder.cdef('typedef UInt32 CPpmd_State_Ref;')
    ffibuilder.cdef('typedef UInt32 CPpmd_Void_Ref;')
else:
    ffibuilder.cdef('typedef CPpmd_State * CPpmd_State_Ref;')
    ffibuilder.cdef('typedef void * CPpmd_Void_Ref;')

# Ppmd7.h
ffibuilder.cdef(r'''
struct CPpmd7_Context_;
''')

if is_64bit():
    ffibuilder.cdef('typedef UInt32 CPpmd7_Context_Ref;')
else:
    ffibuilder.cdef('typedef struct CPpmd7_Context_ CPpmd7_Context_Ref;')

ffibuilder.cdef(r'''
typedef struct CPpmd7_Context_
{
  UInt16 NumStats;
  UInt16 SummFreq;
  CPpmd_State_Ref Stats;
  CPpmd7_Context_Ref Suffix;
} CPpmd7_Context;
''')
ffibuilder.cdef(r'''
typedef struct
{
  CPpmd7_Context *MinContext, *MaxContext;
  CPpmd_State *FoundState;
  unsigned OrderFall, InitEsc, PrevSuccess, MaxOrder, HiBitsFlag;
  Int32 RunLength, InitRL;

  UInt32 Size;
  UInt32 GlueCount;
  Byte *Base, *LoUnit, *HiUnit, *Text, *UnitsStart;
  UInt32 AlignOffset;

  Byte Indx2Units[38];
  Byte Units2Indx[128];
  CPpmd_Void_Ref FreeList[38];
  Byte NS2Indx[256], NS2BSIndx[256], HB2Flag[256];
  CPpmd_See DummySee, See[25][16];
  UInt16 BinSumm[128][64];
} CPpmd7;
''')

# ----------- API ---------------------
ffibuilder.cdef(r'''
typedef struct
{
  UInt32 Range;
  UInt32 Code;
  IByteIn *Stream;
} CPpmd7z_RangeDec;
''')
ffibuilder.cdef(r'''
typedef struct
{
  UInt64 Low;
  UInt32 Range;
  Byte Cache;
  UInt64 CacheSize;
  IByteOut *Stream;
} CPpmd7z_RangeEnc;
''')
ffibuilder.cdef(r'''
typedef struct {
    /* Inherits from IByteOut */
    void (*Write)(void *p, Byte b);
    char *buf;
    int size;
    int pos;
} BufferWriter;

typedef struct {
    /* Inherits from IByteIn */
    Byte (*Read)(void *p);
    char *buf;
    int size;
    int pos;
} BufferReader;
''')
ffibuilder.cdef(r'''
void ppmd_state_init(CPpmd7 *ppmd, unsigned int maxOrder, unsigned int memSize);
void ppmd_state_close(CPpmd7 *ppmd);
void ppmd_decompress_init(CPpmd7z_RangeDec *rc, BufferReader *reader);
void ppmd_compress_init(CPpmd7z_RangeEnc *rc, BufferWriter *write);

void Ppmd7_Construct(CPpmd7 *p);
void Ppmd7_Init(CPpmd7 *p, unsigned maxOrder);
int Ppmd7_DecodeSymbol(CPpmd7 *p, CPpmd7z_RangeDec *rc);

void Ppmd7z_RangeEnc_Init(CPpmd7z_RangeEnc *p);
void Ppmd7z_RangeEnc_FlushData(CPpmd7z_RangeEnc *p);
void Ppmd7_EncodeSymbol(CPpmd7 *p, CPpmd7z_RangeEnc *rc, int symbol);
''')
# -------------------------------------
ffibuilder.set_source('_ppmd', r'''
#include "Ppmd7.h"
#include <stdio.h>
#include <stdlib.h>

#ifdef _WIN32
#define getc_unlocked fgetc
#define putc_unlocked fputc
#endif

static void *pmalloc(ISzAllocPtr ip, size_t size)
{
    (void) ip;
    return malloc(size);
}

static void pfree(ISzAllocPtr ip, void *addr)
{
    (void) ip;
    free(addr);
}

static ISzAlloc allocator = { pmalloc, pfree };

typedef struct {
    /* Inherits from IByteOut */
    void (*Write)(void *p, Byte b);
    char *buf;
    int size;
    int pos;
} BufferWriter;

typedef struct {
    /* Inherits from IByteIn */
    Byte (*Read)(void *p);
    char *buf;
    int size;
    int pos;
} BufferReader;

static void Write(void *p, Byte b)
{
    BufferWriter *bw = p;
    if (bw->pos >= bw->size)
        return;
    bw->buf[bw->pos] = b;
    bw->pos++;
}

static Byte Read(void *p)
{
    BufferReader *br = p;
	if (br->pos > br->size) {
	    return 0;
    }
	int c = br->buf[br->pos];
	br->pos++;
    return c;
}

void ppmd_state_init(CPpmd7 *p, unsigned int maxOrder, unsigned int memSize)
{
    Ppmd7_Construct(p);
    Ppmd7_Alloc(p, memSize, &allocator);
    Ppmd7_Init(p, maxOrder);
}

void ppmd_state_close(CPpmd7 *ppmd)
{
    Ppmd7_Free(ppmd, &allocator);
}

void ppmd_compress_init(CPpmd7z_RangeEnc *rc, BufferWriter *writer)
{
    writer->Write = Write;
    rc->Stream = (IByteOut *) writer;
    Ppmd7z_RangeEnc_Init(rc);
}

int ppmd_decompress_init(CPpmd7z_RangeDec *rc, BufferReader *reader)
{
    reader->Read = Read;
    rc->Stream = (IByteIn *) reader;
    Bool res = Ppmd7z_RangeDec_Init(rc);
    return res;
}
''', sources=sources, include_dirs=[SRC_ROOT])

if __name__ == "__main__":  # not when running with setuptools
    ffibuilder.compile(verbose=True)
