#include "Ppmd7.h"
#include "Ppmd8.h"

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
    void (*dst_write)(char *buf, int size, void *userdata);
    void *userdata;
} RawWriter;

typedef struct {
    /* Inherits from IByteIn */
    Byte (*Read)(void *p);
    int (*src_readinto)(char *buf, int size, void *userdata);
    void *userdata;
} RawReader;

// ppmd7
void ppmd_state_init(CPpmd7 *ppmd, unsigned int maxOrder, unsigned int memSize);
void ppmd_state_close(CPpmd7 *ppmd);
int ppmd_decompress_init(CPpmd7z_RangeDec *rc, RawReader *reader, int (*src_readingo)(char *, int, void*), void *userdata);
void ppmd_compress_init(CPpmd7z_RangeEnc *rc, RawWriter *write, void (*dst_write)(char *, int, void*), void *userdata);

void Ppmd7_Construct(CPpmd7 *p);
void Ppmd7_Init(CPpmd7 *p, unsigned maxOrder);
int Ppmd7_DecodeSymbol(CPpmd7 *p, CPpmd7z_RangeDec *rc);

void Ppmd7z_RangeEnc_Init(CPpmd7z_RangeEnc *p);
void Ppmd7z_RangeEnc_FlushData(CPpmd7z_RangeEnc *p);
void Ppmd7_EncodeSymbol(CPpmd7 *p, CPpmd7z_RangeEnc *rc, int symbol);

// ppmd8
void ppmd8_state_init(CPpmd8 *p, unsigned int maxOrder, unsigned int memSize, unsigned int restore);
void ppmd8_state_close(CPpmd8 *p);

Bool Ppmd8_RangeDec_Init(CPpmd8 *p);
void Ppmd8_Init(CPpmd8 *p, unsigned maxOrder, unsigned restoreMethod);
int Ppmd8_DecodeSymbol(CPpmd8 *p);

void Ppmd8_RangeEnc_FlushData(CPpmd8 *p);
void Ppmd8_EncodeSymbol(CPpmd8 *p, int symbol);
