import cffi
import pathlib
import sys


def is_64bit() -> bool:
    return sys.maxsize > 2**32


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

# ------------- Decode ----------------
ffibuilder.cdef(r'''
typedef struct
{
  UInt32 Range;
  UInt32 Code;
  IByteIn *Stream;
} CPpmd7z_RangeDec;
''')
# ------------- Encode ----------------
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
int ppmd_state_init(unsigned int maxOrder, unsigned int memSize, CPpmd7 *ppmd);
int ppmd_decompress_init(FILE *file, CPpmd7z_RangeDec *rc);
void ppmd_decompress_close(CPpmd7 *ppmd);
int Ppmd7_DecodeSymbol(CPpmd7 *p, CPpmd7z_RangeDec *rc);
''')


# -------------------------------------
ffibuilder.set_source('_ppmd', r'''
#include "Ppmd7.h"
#include <stdio.h>
#include <stdlib.h>

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

struct CharWriter {
    /* Inherits from IByteOut */
    void (*Write)(void *p, Byte b);
    FILE *fp;
};

struct CharReader {
    /* Inherits from IByteIn */
    Byte (*Read)(void *p);
    FILE *fp;
    Bool eof;
};

static void Write(void *p, Byte b)
{
    struct CharWriter *cw = p;
    putc_unlocked(b, cw->fp);
}

static Byte Read(void *p)
{
    struct CharReader *cr = p;
    if (cr->eof)
	    return 0;
    int c = getc_unlocked(cr->fp);
    if (c == EOF) {
	    cr->eof = 1;
	    return 0;
    }
    return c;
}

void ppmd_state_init(unsigned int maxOrder, unsigned int memSize, CPpmd7 *ppmd)
{
    Ppmd7_Alloc(ppmd, memSize, &allocator);
    Ppmd7_Construct(ppmd);
}

void ppmd_decompress_init(FILE *file, CPpmd7z_RangeDec *rc)
{
    Bool res;
    struct CharReader reader = { Read, file, 0 };
    rc->Stream = (IByteIn *) &reader;
    Ppmd7z_RangeDec_Init(rc);
}

int ppmd_decompress(Byte *outbuf, size_t outsize, CPpmd7 *ppmd, CPpmd7z_RangeDec *rc)
{
    size_t i;
    for (i = 0; i < outsize; i++) {
        int sym = Ppmd7_DecodeSymbol(ppmd, rc);
        if (sym < 0) {
            // eof
            break;
        }
        outbuf[i] = (Byte)sym;
    }
    if (!Ppmd7z_RangeDec_IsFinishedOK(rc)) {
        return -1;
    }
    return i;
}

void ppmd_decompress_close(CPpmd7 *ppmd)
{
    Ppmd7_Free(ppmd, &allocator);
}
''', sources=sources, include_dirs=[SRC_ROOT])


if __name__ == "__main__":    # not when running with setuptools
    ffibuilder.compile(verbose=True)
