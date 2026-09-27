#include "MForgeDisplay.h"
#include <stdlib.h>

// =====================================================
// Init
// =====================================================

void MForgeDisplay::begin()
{
    MForgeDriver::begin();

    _fg = CRGB(MATRIXFORGE_DEFAULT_FG_R, MATRIXFORGE_DEFAULT_FG_G, MATRIXFORGE_DEFAULT_FG_B);
    _bg = CRGB(MATRIXFORGE_DEFAULT_BG_R, MATRIXFORGE_DEFAULT_BG_G, MATRIXFORGE_DEFAULT_BG_B);
    _brightness = MATRIXFORGE_BRIGHTNESS;
    _curX = 0;
    _curY = 0;

    clearDisplay();
    show();
}

// =====================================================
// Buffer control
// =====================================================

void MForgeDisplay::show()
{
    MForgeDriver::show(_leds, MATRIXFORGE_NUM_LEDS, _brightness);
}

void MForgeDisplay::clearDisplay()
{
    fill_solid(_leds, MATRIXFORGE_NUM_LEDS, CRGB::Black);
}

void MForgeDisplay::fillDisplay(uint8_t r, uint8_t g, uint8_t b)
{
    fill_solid(_leds, MATRIXFORGE_NUM_LEDS, CRGB(r, g, b));
}

void MForgeDisplay::pushCanvas()
{
    memcpy(_savedCanvas, _leds, sizeof(_leds));
}

void MForgeDisplay::popCanvas()
{
    memcpy(_leds, _savedCanvas, sizeof(_leds));
}

// =====================================================
// Color / cursor state
// =====================================================

void MForgeDisplay::setFgColor(uint8_t r, uint8_t g, uint8_t b) { _fg = CRGB(r,g,b); }
void MForgeDisplay::setBgColor(uint8_t r, uint8_t g, uint8_t b) { _bg = CRGB(r,g,b); }
void MForgeDisplay::setCursor(int16_t x, int16_t y) { _curX = x; _curY = y; }

// =====================================================
// Internal helpers
// =====================================================

bool MForgeDisplay::_inBounds(int16_t x, int16_t y) const
{
    return x >= 0 && x < MATRIXFORGE_GRID_WIDTH &&
           y >= 0 && y < MATRIXFORGE_GRID_HEIGHT;
}

uint16_t MForgeDisplay::_xyToIndex(int16_t x, int16_t y) const
{
    uint8_t Qx = (uint8_t)x / 8;
    uint8_t Qy = (uint8_t)y / 8;

    uint16_t base =
          128 * (1 - Qx) * (1 - Qy)
        +  64 *      Qx  * (1 - Qy)
        + 192 * (1 - Qx) *      Qy;

    return base + (7 - (uint8_t)y % 8) * 8 + (7 - (uint8_t)x % 8);
}

void MForgeDisplay::_writePixel(int16_t x, int16_t y, CRGB color)
{
    if (!_inBounds(x, y)) return;
    _leds[_xyToIndex(x, y)] = color;
}

// =====================================================
// Primitives
// =====================================================

void MForgeDisplay::drawPixel(int16_t x, int16_t y)
    { _writePixel(x, y, _fg); }

void MForgeDisplay::drawPixel(int16_t x, int16_t y, uint8_t r, uint8_t g, uint8_t b)
    { _writePixel(x, y, CRGB(r,g,b)); }

void MForgeDisplay::drawPixel(int16_t x, int16_t y, CRGB color)
    { _writePixel(x, y, color); }

// --- Line (Bresenham) ---
void MForgeDisplay::drawLine(int16_t x0, int16_t y0, int16_t x1, int16_t y1)
    { drawLine(x0,y0,x1,y1,_fg.r,_fg.g,_fg.b); }

void MForgeDisplay::drawLine(int16_t x0, int16_t y0, int16_t x1, int16_t y1,
                              uint8_t r, uint8_t g, uint8_t b)
{
    CRGB col(r,g,b);
    int16_t dx =  abs(x1-x0), sx = x0<x1 ? 1:-1;
    int16_t dy = -abs(y1-y0), sy = y0<y1 ? 1:-1;
    int16_t err = dx+dy;
    while (true) {
        _writePixel(x0,y0,col);
        if (x0==x1 && y0==y1) break;
        int16_t e2 = 2*err;
        if (e2 >= dy) { err+=dy; x0+=sx; }
        if (e2 <= dx) { err+=dx; y0+=sy; }
    }
}

// --- Rect ---
void MForgeDisplay::drawRect(int16_t x, int16_t y, int16_t w, int16_t h)
    { drawRect(x,y,w,h,_fg.r,_fg.g,_fg.b); }

void MForgeDisplay::drawRect(int16_t x, int16_t y, int16_t w, int16_t h,
                              uint8_t r, uint8_t g, uint8_t b)
{
    drawLine(x,     y,     x+w-1, y,     r,g,b);
    drawLine(x+w-1, y,     x+w-1, y+h-1, r,g,b);
    drawLine(x,     y+h-1, x+w-1, y+h-1, r,g,b);
    drawLine(x,     y,     x,     y+h-1, r,g,b);
}

void MForgeDisplay::fillRect(int16_t x, int16_t y, int16_t w, int16_t h)
    { fillRect(x,y,w,h,_fg.r,_fg.g,_fg.b); }

void MForgeDisplay::fillRect(int16_t x, int16_t y, int16_t w, int16_t h,
                              uint8_t r, uint8_t g, uint8_t b)
{
    CRGB col(r,g,b);
    for (int16_t row=y; row<y+h; ++row)
        for (int16_t col2=x; col2<x+w; ++col2)
            _writePixel(col2, row, col);
}

// --- Circle (Bresenham midpoint) ---
void MForgeDisplay::_circlePoints(int16_t cx, int16_t cy,
                                   int16_t dx, int16_t dy, CRGB c)
{
    _writePixel(cx+dx, cy+dy, c); _writePixel(cx-dx, cy+dy, c);
    _writePixel(cx+dx, cy-dy, c); _writePixel(cx-dx, cy-dy, c);
    _writePixel(cx+dy, cy+dx, c); _writePixel(cx-dy, cy+dx, c);
    _writePixel(cx+dy, cy-dx, c); _writePixel(cx-dy, cy-dx, c);
}

void MForgeDisplay::drawCircle(int16_t cx, int16_t cy, int16_t radius)
    { drawCircle(cx,cy,radius,_fg.r,_fg.g,_fg.b); }

void MForgeDisplay::drawCircle(int16_t cx, int16_t cy, int16_t radius,
                                uint8_t r, uint8_t g, uint8_t b)
{
    CRGB col(r,g,b);
    int16_t dx=0, dy=radius, err=1-radius;
    while (dx<=dy) {
        _circlePoints(cx,cy,dx,dy,col);
        if (err<0) err+=2*dx+3; else { err+=2*(dx-dy)+5; --dy; }
        ++dx;
    }
}

void MForgeDisplay::_hLine(int16_t x0, int16_t x1, int16_t y, CRGB c)
{
    if (x0>x1) { int16_t t=x0; x0=x1; x1=t; }
    for (int16_t x=x0; x<=x1; ++x) _writePixel(x, y, c);
}

void MForgeDisplay::fillCircle(int16_t cx, int16_t cy, int16_t radius)
    { fillCircle(cx,cy,radius,_fg.r,_fg.g,_fg.b); }

void MForgeDisplay::fillCircle(int16_t cx, int16_t cy, int16_t radius,
                                uint8_t r, uint8_t g, uint8_t b)
{
    CRGB col(r,g,b);
    int16_t dx=0, dy=radius, err=1-radius;
    while (dx<=dy) {
        _hLine(cx-dy, cx+dy, cy+dx, col);
        _hLine(cx-dy, cx+dy, cy-dx, col);
        _hLine(cx-dx, cx+dx, cy+dy, col);
        _hLine(cx-dx, cx+dx, cy-dy, col);
        if (err<0) err+=2*dx+3; else { err+=2*(dx-dy)+5; --dy; }
        ++dx;
    }
}

// --- Triangle ---
void MForgeDisplay::drawTriangle(int16_t x0, int16_t y0,
                                  int16_t x1, int16_t y1,
                                  int16_t x2, int16_t y2)
    { drawTriangle(x0,y0,x1,y1,x2,y2,_fg.r,_fg.g,_fg.b); }

void MForgeDisplay::drawTriangle(int16_t x0, int16_t y0,
                                  int16_t x1, int16_t y1,
                                  int16_t x2, int16_t y2,
                                  uint8_t r, uint8_t g, uint8_t b)
{
    drawLine(x0,y0,x1,y1,r,g,b);
    drawLine(x1,y1,x2,y2,r,g,b);
    drawLine(x2,y2,x0,y0,r,g,b);
}

// --- Flood fill (iterative, 4-connected) ---
void MForgeDisplay::floodFill(int16_t x, int16_t y, uint8_t r, uint8_t g, uint8_t b)
{
    if (!_inBounds(x,y)) return;
    CRGB newC(r,g,b);
    CRGB oldC = _leds[_xyToIndex(x,y)];
    if (oldC == newC) return;

    uint16_t stack[MATRIXFORGE_NUM_LEDS];
    uint16_t top = 0;
    stack[top++] = (uint16_t)(x | (y<<8));

    while (top > 0) {
        uint16_t v  = stack[--top];
        int16_t  cx = v & 0xFF;
        int16_t  cy = (v >> 8) & 0xFF;
        if (!_inBounds(cx,cy)) continue;
        if (_leds[_xyToIndex(cx,cy)] != oldC) continue;
        _writePixel(cx,cy,newC);
        if (top+4 <= MATRIXFORGE_NUM_LEDS) {
            stack[top++] = (uint16_t)((cx+1)|(cy<<8));
            stack[top++] = (uint16_t)((cx-1)|(cy<<8));
            stack[top++] = (uint16_t)( cx   |((cy+1)<<8));
            stack[top++] = (uint16_t)( cx   |((cy-1)<<8));
        }
    }
}

// =====================================================
// Bitmap
// =====================================================

void MForgeDisplay::drawBitmap(int16_t x, int16_t y,
                                const CRGB* bitmap, uint8_t w, uint8_t h)
{
    for (uint8_t row=0; row<h; ++row)
        for (uint8_t col=0; col<w; ++col)
            _writePixel(x+col, y+row, bitmap[row*w+col]);
}

void MForgeDisplay::drawBitmap1bit(int16_t x, int16_t y,
                                    const uint8_t* bits, uint8_t w, uint8_t h,
                                    bool bgTransparent)
{
    for (uint8_t row=0; row<h; ++row) {
        for (uint8_t col=0; col<w; ++col) {
            uint8_t byteIdx = (row*w+col)/8;
            uint8_t bitIdx  = 7-((row*w+col)%8);
            bool    set     = (bits[byteIdx] >> bitIdx) & 1;
            if (set)                _writePixel(x+col, y+row, _fg);
            else if(!bgTransparent) _writePixel(x+col, y+row, _bg);
        }
    }
}

// =====================================================
// Sprite
// =====================================================

void MForgeDisplay::drawSprite(const MForgeSprite& sprite, int16_t x, int16_t y)
{
    for (uint8_t row=0; row<sprite.height(); ++row)
        for (uint8_t col=0; col<sprite.width(); ++col)
            if (!sprite.isTransparent(col,row))
                _writePixel(x+col, y+row, sprite.getPixel(col,row));
}

// =====================================================
// Font / Text
// =====================================================

void MForgeDisplay::drawChar(char c, bool bgTransparent)
{
    drawChar(_curX, _curY, c, bgTransparent);
    _curX += MATRIXFORGE_FONT_W + MATRIXFORGE_FONT_SPACING;
}

void MForgeDisplay::drawChar(int16_t x, int16_t y, char c, bool bgTransparent)
{
    const uint8_t* glyph = MForgeFont::getGlyph(c);
    if (!glyph) return;
    for (uint8_t row=0; row<MATRIXFORGE_FONT_H; ++row) {
        uint8_t rowBits = pgm_read_byte(&glyph[row]);
        for (uint8_t col=0; col<MATRIXFORGE_FONT_W; ++col) {
            bool on = (rowBits >> (7-col)) & 1;
            if (on)                _writePixel(x+col, y+row, _fg);
            else if(!bgTransparent) _writePixel(x+col, y+row, _bg);
        }
    }
}

void MForgeDisplay::drawText(const char* str, bool bgTransparent)
{
    while (*str) drawChar(*str++, bgTransparent);
}

void MForgeDisplay::drawText(int16_t x, int16_t y, const char* str, bool bgTransparent)
{
    setCursor(x,y);
    drawText(str, bgTransparent);
}

void MForgeDisplay::drawTextWrapped(int16_t x, int16_t y, const char* str, bool bgTransparent)
{
    setCursor(x,y);
    while (*str) {
        char c = *str++;
        if (c == '\n') { _curX=x; _curY+=MATRIXFORGE_FONT_H+1; continue; }
        if (_curX+MATRIXFORGE_FONT_W > MATRIXFORGE_GRID_WIDTH) { _curX=x; _curY+=MATRIXFORGE_FONT_H+1; }
        drawChar(c, bgTransparent);
    }
}

int16_t MForgeDisplay::textWidth(const char* str) const
{
    int16_t n=0;
    while(*str++) ++n;
    return n>0 ? n*MATRIXFORGE_FONT_W+(n-1)*MATRIXFORGE_FONT_SPACING : 0;
}
