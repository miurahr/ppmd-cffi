#include "Ppmd7.h"
#include "Ppmd8.h"

#include <stdio.h>
#include <stdlib.h>

#ifdef _WIN32
#define getc_unlocked fgetc
#define putc_unlocked fputc
#endif

typedef struct {
    void (*Write)(void *p, Byte b);
    void (*dst_write)(char *buf, int size, void *userdata);
    void *userdata;
} RawWriter;

typedef struct {
    Byte (*Read)(void *p);
    int (*src_readinto)(char *buf, int size, void *userdata);
    void *userdata;
} RawReader;

// ppmd7
void ppmd_state_init(CPpmd7 *ppmd, unsigned int maxOrder, unsigned int memSize, ISzAlloc *allocator);
void ppmd_state_close(CPpmd7 *ppmd, ISzAlloc *allocator);
int ppmd_decompress_init(CPpmd7z_RangeDec *rc, RawReader *reader, int (*src_readingo)(char *, int, void*), void *userdata);
void ppmd_compress_init(CPpmd7z_RangeEnc *rc, RawWriter *write, void (*dst_write)(char *, int, void*), void *userdata);

void Ppmd7_Construct(CPpmd7 *p);
void Ppmd7_Init(CPpmd7 *p, unsigned maxOrder);
int Ppmd7_DecodeSymbol(CPpmd7 *p, CPpmd7z_RangeDec *rc);

void Ppmd7z_RangeEnc_Init(CPpmd7z_RangeEnc *p);
void Ppmd7z_RangeEnc_FlushData(CPpmd7z_RangeEnc *p);
void Ppmd7_EncodeSymbol(CPpmd7 *p, CPpmd7z_RangeEnc *rc, int symbol);

// ppmd8
void ppmd8_malloc(CPpmd8 *p, unsigned int memSize, ISzAlloc *allocator);
void ppmd8_free(CPpmd8 *p, ISzAlloc *allocator);

Bool Ppmd8_RangeDec_Init(CPpmd8 *p);
void Ppmd8_Init(CPpmd8 *p, unsigned maxOrder, unsigned restoreMethod);
int Ppmd8_DecodeSymbol(CPpmd8 *p);

void Ppmd8_RangeEnc_FlushData(CPpmd8 *p);
void Ppmd8_EncodeSymbol(CPpmd8 *p, int symbol);
