#include "PixelFightGame.h"
#include <math.h>
#include <stdio.h>
#include <string.h>

PixelFightGame::PixelFightGame()
{
    p1X = 7;
    p2X = 7;

    p1Score = 0;
    p2Score = 0;

    gameOver = false;
    winner = 0;

    bulletP1.active = false;
    bulletP2.active = false;

    lastShotP1 = 0;
    lastShotP2 = 0;

    winAnimStart   = 0;
    lastOledUpdate = 0;
}

void PixelFightGame::begin()
{
    pinMode(P1_LEFT_PIN,  INPUT_PULLUP);
    pinMode(P1_RIGHT_PIN, INPUT_PULLUP);
    pinMode(P1_MENU_PIN,  INPUT_PULLUP);
    pinMode(P1_UP_PIN,    INPUT_PULLUP);

    pinMode(P2_LEFT_PIN,  INPUT_PULLUP);
    pinMode(P2_RIGHT_PIN, INPUT_PULLUP);
    pinMode(P2_MENU_PIN,  INPUT_PULLUP);
    pinMode(P2_UP_PIN,    INPUT_PULLUP);

    display.begin();

    oled.begin(OLED_I2C_ADDRESS, true);
    showSplashOLED();

    resetGame();
}

void PixelFightGame::resetGame()
{
    p1X = 7;
    p2X = 7;

    p1Score = 0;
    p2Score = 0;

    gameOver = false;
    winner   = 0;
    winAnimStart = 0;

    bulletP1.active = false;
    bulletP2.active = false;
    bulletP1.x = 0;  bulletP1.y = 0;
    bulletP2.x = 0;  bulletP2.y = 0;

    for (int x = 0; x < 16; x++)
        for (int y = 0; y < 7; y++)
        {
            p1Territory[x][y] = CELL_INTACT;
            p2Territory[x][y] = CELL_INTACT;
        }

    lastOledUpdate = 0;
    updateScoreOLED();
}

bool PixelFightGame::pressed(uint8_t pin)
{
    return digitalRead(pin) == LOW;
}

void PixelFightGame::update()
{
    if (gameOver)
    {
        if (pressed(P1_UP_PIN) || pressed(P2_UP_PIN))
        {
            delay(200);
            resetGame();
        }
        return;
    }

    updateInputs();
    updateBullets();
    checkVictory();
    updateScoreOLED();
}

void PixelFightGame::updateInputs()
{
    // Edge-triggered movement: one step per button press, not while held.
    static bool prevP1L = false, prevP1R = false, prevP1M = false;
    static bool prevP2L = false, prevP2R = false, prevP2M = false;
    static uint32_t lastP1L = 0, lastP1R = 0;
    static uint32_t lastP2L = 0, lastP2R = 0;

    const bool nowP1L = pressed(P1_LEFT_PIN);
    const bool nowP1R = pressed(P1_RIGHT_PIN);
    const bool nowP1M = pressed(P1_MENU_PIN);
    const bool nowP2L = pressed(P2_LEFT_PIN);
    const bool nowP2R = pressed(P2_RIGHT_PIN);
    const bool nowP2M = pressed(P2_MENU_PIN);

    const uint32_t now = millis();

    if (nowP1L && !prevP1L && p1X > 0 && (now - lastP1L) >= MOVE_DEBOUNCE_MS)
    {
        p1X--;
        lastP1L = now;
    }
    if (nowP1R && !prevP1R && p1X < 15 && (now - lastP1R) >= MOVE_DEBOUNCE_MS)
    {
        p1X++;
        lastP1R = now;
    }
    if (nowP2L && !prevP2L && p2X > 0 && (now - lastP2L) >= MOVE_DEBOUNCE_MS)
    {
        p2X--;
        lastP2L = now;
    }
    if (nowP2R && !prevP2R && p2X < 15 && (now - lastP2R) >= MOVE_DEBOUNCE_MS)
    {
        p2X++;
        lastP2R = now;
    }

    if (nowP1M && !prevP1M) fireP1();
    if (nowP2M && !prevP2M) fireP2();

    prevP1L = nowP1L;
    prevP1R = nowP1R;
    prevP1M = nowP1M;
    prevP2L = nowP2L;
    prevP2R = nowP2R;
    prevP2M = nowP2M;
}

void PixelFightGame::fireP1()
{
    if (bulletP1.active) return;
    if (millis() - lastShotP1 < SHOOT_COOLDOWN) return;

    bulletP1.active = true;
    bulletP1.x      = p1X;
    bulletP1.y      = 1;
    bulletP1.dir    = 1;
    bulletP1.owner  = TEAM_BLUE;
    lastShotP1      = millis();
}

void PixelFightGame::fireP2()
{
    if (bulletP2.active) return;
    if (millis() - lastShotP2 < SHOOT_COOLDOWN) return;

    bulletP2.active = true;
    bulletP2.x      = p2X;
    bulletP2.y      = 14;
    bulletP2.dir    = -1;
    bulletP2.owner  = TEAM_RED;
    lastShotP2      = millis();
}

// =====================================================
// Damage helpers
// =====================================================

void PixelFightGame::damageP1(uint8_t col)
{
    // Red attacks from below — peel bottom-most intact pixel first.
    for (int y = 6; y >= 0; y--)
    {
        if (p1Territory[col][y] == CELL_INTACT)
        {
            p1Territory[col][y] = CELL_HIT_BY_RED;
            p2Score++;
            return;
        }
    }
}

void PixelFightGame::damageP2(uint8_t col)
{
    // Blue attacks from above — peel top-most intact pixel first.
    for (int y = 0; y < 7; y++)
    {
        if (p2Territory[col][y] == CELL_INTACT)
        {
            p2Territory[col][y] = CELL_HIT_BY_BLUE;
            p1Score++;
            return;
        }
    }
}

void PixelFightGame::repairP1(uint8_t col)
{
    // Heal the destroyed pixel on the battlefront — the hole touching intact territory.
    for (int y = 0; y < 7; y++)
        if (p1Territory[col][y] != CELL_INTACT)
            if (y == 0 || p1Territory[col][y - 1] == CELL_INTACT)
                { p1Territory[col][y] = CELL_INTACT; return; }

    // Column fully gone — regrow from the player side.
    for (int y = 0; y < 7; y++)
        if (p1Territory[col][y] != CELL_INTACT)
            { p1Territory[col][y] = CELL_INTACT; return; }
}

void PixelFightGame::repairP2(uint8_t col)
{
    // Heal the destroyed pixel on the battlefront — the hole touching intact territory.
    for (int y = 6; y >= 0; y--)
        if (p2Territory[col][y] != CELL_INTACT)
            if (y == 6 || p2Territory[col][y + 1] == CELL_INTACT)
                { p2Territory[col][y] = CELL_INTACT; return; }

    // Column fully gone — regrow from the player side.
    for (int y = 6; y >= 0; y--)
        if (p2Territory[col][y] != CELL_INTACT)
            { p2Territory[col][y] = CELL_INTACT; return; }
}

// =====================================================
// Bullet movement
// =====================================================

void PixelFightGame::updateBullets()
{
    static uint32_t lastBulletMove = 0;
    if (millis() - lastBulletMove < 40) return;
    lastBulletMove = millis();

    if (bulletP1.active)
    {
        bulletP1.y++;

        if (bulletP1.y >= 8)
        {
            bool hadDamage = false;
            for (int y = 0; y < 7; y++)
                if (p1Territory[bulletP1.x][y] != CELL_INTACT)
                    { hadDamage = true; break; }

            if (hadDamage)
                repairP1(bulletP1.x);
            else
                damageP2(bulletP1.x);

            bulletP1.active = false;
        }
    }

    if (bulletP2.active)
    {
        bulletP2.y--;

        if (bulletP2.y <= 7)
        {
            bool hadDamage = false;
            for (int y = 0; y < 7; y++)
                if (p2Territory[bulletP2.x][y] != CELL_INTACT)
                    { hadDamage = true; break; }

            if (hadDamage)
                repairP2(bulletP2.x);
            else
                damageP1(bulletP2.x);

            bulletP2.active = false;
        }
    }
}

// =====================================================
// Victory
// =====================================================

bool PixelFightGame::columnDestroyedP1(uint8_t col)
{
    for (int y = 0; y < 7; y++)
        if (p1Territory[col][y] == CELL_INTACT) return false;
    return true;
}

bool PixelFightGame::columnDestroyedP2(uint8_t col)
{
    for (int y = 0; y < 7; y++)
        if (p2Territory[col][y] == CELL_INTACT) return false;
    return true;
}

void PixelFightGame::checkVictory()
{
    for (int x = 0; x < 16; x++)
    {
        if (columnDestroyedP1(x))
        {
            winner       = TEAM_RED;
            gameOver     = true;
            winAnimStart = millis();
            showWinnerOLED();
            return;
        }
        if (columnDestroyedP2(x))
        {
            winner       = TEAM_BLUE;
            gameOver     = true;
            winAnimStart = millis();
            showWinnerOLED();
            return;
        }
    }
}

// =====================================================
// OLED UI helpers  (128×64 SH1106)
// =====================================================

void PixelFightGame::oledPrintCentered(int16_t areaX, int16_t areaW, int16_t y,
                                       uint8_t textSize, const char* text)
{
    oled.setTextSize(textSize);
    int16_t tw = (int16_t)strlen(text) * 6 * textSize;
    int16_t tx = areaX + (areaW - tw) / 2;
    if (tx < areaX) tx = areaX;
    oled.setCursor(tx, y);
    oled.print(text);
}

void PixelFightGame::oledPrintCentered(int16_t areaX, int16_t areaW, int16_t y,
                                       uint8_t textSize, uint16_t value)
{
    char buf[6];
    snprintf(buf, sizeof(buf), "%u", value);
    oledPrintCentered(areaX, areaW, y, textSize, buf);
}

void PixelFightGame::oledDrawHudFrame()
{
    oled.setTextColor(SH110X_WHITE);
    oledPrintCentered(0, OLED_WIDTH, 0, 1, "PIXEL FIGHT");

    oled.drawFastHLine(0, 10, OLED_WIDTH, SH110X_WHITE);
    oled.drawFastVLine(64, 10, OLED_HEIGHT - 10, SH110X_WHITE);
}

void PixelFightGame::oledDrawOddsBar(int16_t x, int16_t y, int16_t w, int16_t h, uint8_t pct)
{
    if (pct > 100) pct = 100;
    oled.drawRect(x, y, w, h, SH110X_WHITE);
    int16_t fillW = (int16_t)((w - 2) * pct / 100);
    if (fillW > 0)
        oled.fillRect(x + 1, y + 1, fillW, h - 2, SH110X_WHITE);
}

void PixelFightGame::showSplashOLED()
{
    oled.clearDisplay();
    oled.setTextColor(SH110X_WHITE);
    oledPrintCentered(0, OLED_WIDTH, 18, 2, "PIXEL");
    oledPrintCentered(0, OLED_WIDTH, 38, 2, "FIGHT");
    oled.display();
}

// =====================================================
// OLED HUD
// =====================================================

void PixelFightGame::computeWinChance(uint8_t& bluePct, uint8_t& redPct) const
{
    uint32_t bluePower = 0;
    uint32_t redPower  = 0;

    for (int col = 0; col < 16; col++)
    {
        uint8_t blueDepth = 0;
        uint8_t redDepth  = 0;

        for (int y = 0; y < 7; y++)
        {
            if (p1Territory[col][y] == CELL_INTACT) blueDepth++;
            if (p2Territory[col][y] == CELL_INTACT) redDepth++;
        }

        uint8_t bluePen = 7 - redDepth;
        uint8_t redPen  = 7 - blueDepth;

        int dBlue = abs(col - p1X);
        int dRed  = abs(col - p2X);
        if (dBlue > 15) dBlue = 15;
        if (dRed  > 15) dRed  = 15;

        uint8_t wBlue = 16 - dBlue;
        uint8_t wRed  = 16 - dRed;

        bluePower += (uint32_t)blueDepth * wBlue;
        bluePower += (uint32_t)bluePen * wBlue;
        redPower  += (uint32_t)redDepth * wRed;
        redPower  += (uint32_t)redPen * wRed;

        // Imminent column collapse weighs heavily at the active front.
        if (blueDepth == 1) redPower  += (uint32_t)wBlue * 24;
        if (blueDepth == 0) redPower  += (uint32_t)wBlue * 48;
        if (redDepth  == 1) bluePower += (uint32_t)wRed  * 24;
        if (redDepth  == 0) bluePower += (uint32_t)wRed  * 48;
    }

    uint32_t total = bluePower + redPower;
    if (total == 0)
    {
        bluePct = 50;
        redPct  = 50;
        return;
    }

    bluePct = (uint8_t)((bluePower * 100UL) / total);
    if (bluePct > 100) bluePct = 100;
    redPct = 100 - bluePct;
}

void PixelFightGame::updateScoreOLED()
{
    if (gameOver) return;
    if (millis() - lastOledUpdate < 200) return;
    lastOledUpdate = millis();

    uint8_t bluePct, redPct;
    computeWinChance(bluePct, redPct);

    char oddsBlue[10];
    char oddsRed[10];
    snprintf(oddsBlue, sizeof(oddsBlue), "WIN %u%%", bluePct);
    snprintf(oddsRed,  sizeof(oddsRed),  "WIN %u%%", redPct);

    oled.clearDisplay();
    oledDrawHudFrame();

    // Team labels — each half is 64 px wide
    oledPrintCentered(0,  64, 14, 1, "BLUE");
    oledPrintCentered(64, 64, 14, 1, "RED");

    // Kill scores — large, centered per column
    oledPrintCentered(0,  64, 22, 2, p1Score);
    oledPrintCentered(64, 64, 22, 2, p2Score);

    // Win odds text
    oledPrintCentered(0,  64, 40, 1, oddsBlue);
    oledPrintCentered(64, 64, 40, 1, oddsRed);

    // Odds bars — inset inside each panel
    oledDrawOddsBar(6,  52, 52, 8, bluePct);
    oledDrawOddsBar(70, 52, 52, 8, redPct);

    oled.display();
}

void PixelFightGame::showWinnerOLED()
{
    char scoreLine[16];
    snprintf(scoreLine, sizeof(scoreLine), "%u  -  %u", p1Score, p2Score);

    oled.clearDisplay();
    oled.setTextColor(SH110X_WHITE);

    if (winner == TEAM_BLUE)
        oledPrintCentered(0, OLED_WIDTH, 6, 2, "BLUE");
    else
        oledPrintCentered(0, OLED_WIDTH, 6, 2, "RED");

    oledPrintCentered(0, OLED_WIDTH, 26, 2, "WINS!");

    oled.drawFastHLine(16, 44, OLED_WIDTH - 32, SH110X_WHITE);

    oledPrintCentered(0, OLED_WIDTH, 48, 1, scoreLine);
    oledPrintCentered(0, OLED_WIDTH, 56, 1, "UP = RESTART");

    oled.display();
}

// =====================================================
// Rendering (LED matrix)
// =====================================================

void PixelFightGame::drawTerritory()
{
    for (int x = 0; x < 16; x++)
        for (int y = 0; y < 7; y++)
        {
            uint8_t p1 = p1Territory[x][y];
            if (p1 == CELL_INTACT)
                display.drawPixel(x, y + 1, BLUE_BLOCK_R, BLUE_BLOCK_G, BLUE_BLOCK_B);
            else if (p1 == CELL_HIT_BY_RED)
                display.drawPixel(x, y + 1, RED_BLOCK_R, RED_BLOCK_G, RED_BLOCK_B);

            uint8_t p2 = p2Territory[x][y];
            if (p2 == CELL_INTACT)
                display.drawPixel(x, y + 8, RED_BLOCK_R, RED_BLOCK_G, RED_BLOCK_B);
            else if (p2 == CELL_HIT_BY_BLUE)
                display.drawPixel(x, y + 8, BLUE_BLOCK_R, BLUE_BLOCK_G, BLUE_BLOCK_B);
        }
}

void PixelFightGame::drawPlayers()
{
    display.drawPixel(p1X,  0, BLUE_PLAYER_R, BLUE_PLAYER_G, BLUE_PLAYER_B);
    display.drawPixel(p2X, 15, RED_PLAYER_R,  RED_PLAYER_G,  RED_PLAYER_B);
}

void PixelFightGame::drawBullets()
{
    if (bulletP1.active)
        display.drawPixel(bulletP1.x, bulletP1.y, 255, 255, 255);
    if (bulletP2.active)
        display.drawPixel(bulletP2.x, bulletP2.y, 255, 255, 255);
}

void PixelFightGame::renderWinnerAnimation()
{
    unsigned long elapsed = millis() - winAnimStart;

    uint8_t wr, wg, wb;
    if (winner == TEAM_BLUE) { wr = 0;   wg = 0;   wb = 255; }
    else                     { wr = 255; wg = 0;   wb = 0;   }

    const char* msg = (winner == TEAM_BLUE) ? "BLUE WINS!" : "RED WINS!";

    display.clearDisplay();

    // Phase 1 — expanding burst from centre (0–700 ms)
    if (elapsed < 700)
    {
        int radius = (int)((elapsed * 12) / 700);
        for (int r = 0; r <= radius; r++)
            display.drawCircle(8, 7, r, wr, wg, wb);
        if (radius > 1)
            display.fillCircle(8, 7, radius - 1, wr, wg, wb);
    }
    // Phase 2 — scroll winner shout-out (700–2800 ms)
    else if (elapsed < 2800)
    {
        for (int x = 0; x < 16; x++)
            for (int y = 0; y < 16; y++)
                display.drawPixel(x, y, wr / 6, wg / 6, wb / 6);

        int textW   = display.textWidth(msg);
        int scrollX = 16 - (int)((elapsed - 700) / 50);
        if (scrollX < -textW)
            scrollX = -textW;

        display.setFgColor(255, 255, 255);
        display.drawText(scrollX, 5, msg, true);
    }
    // Phase 3 — pulsing hold with centred label (2800 ms+)
    else
    {
        float pulse = 0.45f + 0.55f * (0.5f + 0.5f * sinf((elapsed - 2800) * 0.008f));
        uint8_t pr = (uint8_t)(wr * pulse);
        uint8_t pg = (uint8_t)(wg * pulse);
        uint8_t pb = (uint8_t)(wb * pulse);

        display.fillDisplay(pr, pg, pb);

        const char* team = (winner == TEAM_BLUE) ? "BLU" : "RED";
        display.setFgColor(255, 255, 255);
        display.drawText(1, 3, team, true);
        display.drawText(1, 10, "WIN", true);
    }

    // White restart hint — blink in centre
    if ((elapsed / 400) % 2 == 0)
    {
        display.drawPixel(7, 7, 255, 255, 255);
        display.drawPixel(8, 7, 255, 255, 255);
        display.drawPixel(7, 8, 255, 255, 255);
        display.drawPixel(8, 8, 255, 255, 255);
    }

    display.show();
}

void PixelFightGame::render()
{
    display.clearDisplay();

    if (gameOver)
    {
        renderWinnerAnimation();
        return;
    }

    drawTerritory();
    drawPlayers();
    drawBullets();
    display.show();
}
