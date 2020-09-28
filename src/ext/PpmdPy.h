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
    int (*dst_write)(char *buf, int size);
    char *buf;
    int size;
    int pos;
} BufferWriter;

typedef struct {
    /* Inherits from IByteIn */
    Byte (*Read)(void *p);
    int (*src_readinto)(char *buf, int size, void *userdata);
    void *userdata;
} BufferReader;

void ppmd_state_init(CPpmd7 *ppmd, unsigned int maxOrder, unsigned int memSize);
void ppmd_state_close(CPpmd7 *ppmd);
int ppmd_decompress_init(CPpmd7z_RangeDec *rc, BufferReader *reader, int (*src_readingo)(char *, int, void*), void *userdata);
void ppmd_compress_init(CPpmd7z_RangeEnc *rc, BufferWriter *write);

void Ppmd7_Construct(CPpmd7 *p);
void Ppmd7_Init(CPpmd7 *p, unsigned maxOrder);
int Ppmd7_DecodeSymbol(CPpmd7 *p, CPpmd7z_RangeDec *rc);

void Ppmd7z_RangeEnc_Init(CPpmd7z_RangeEnc *p);
void Ppmd7z_RangeEnc_FlushData(CPpmd7z_RangeEnc *p);
void Ppmd7_EncodeSymbol(CPpmd7 *p, CPpmd7z_RangeEnc *rc, int symbol);
