// =====================================================
// SnakeGame.cpp — Snake game logic implementation
// =====================================================

#include "SnakeGame.h"

// =====================================================
// Constructor
// =====================================================
SnakeGame::SnakeGame(MForgeDisplay& disp, Adafruit_SH1106G& oled)
    : _disp(disp), _oled(oled)
{
}

// =====================================================
// begin() — call once in setup()
// =====================================================
void SnakeGame::begin()
{
    // Configure button pins
    pinMode(SNAKE_BTN_UP,    INPUT_PULLUP);
    pinMode(SNAKE_BTN_DOWN,  INPUT_PULLUP);
    pinMode(SNAKE_BTN_LEFT,  INPUT_PULLUP);
    pinMode(SNAKE_BTN_RIGHT, INPUT_PULLUP);
    pinMode(SNAKE_BTN_MENU,  INPUT_PULLUP);

    // Buzzer
    pinMode(SNAKE_BUZZER_PIN, OUTPUT);
    noTone(SNAKE_BUZZER_PIN);

    // Initial state
    _state = GameState::TITLE;
    _score = 0;

    // Show title screens
    _drawTitleMatrix();
    _oledTitle();
}

// =====================================================
// update() — call every loop()
// =====================================================
void SnakeGame::update()
{
    switch (_state)
    {
        // ── TITLE ─────────────────────────────────
        case GameState::TITLE:
            if (_menuPressed())
            {
                _beepStart();
                _resetGame();
                _state = GameState::PLAYING;
                _lastTick = millis();
            }
            break;

        // ── PLAYING ───────────────────────────────
        case GameState::PLAYING:
            _readButtons();

            if (millis() - _lastTick >= SNAKE_SPEED_MS)
            {
                _lastTick = millis();
                _tick();
            }
            break;

        // ── DEAD ──────────────────────────────────
        case GameState::DEAD:
            if (_menuPressed())
            {
                _beepStart();
                _resetGame();
                _state = GameState::PLAYING;
                _lastTick = millis();
            }
            break;
    }
}

// =====================================================
// _menuPressed() — debounced single-press detection
// =====================================================
bool SnakeGame::_menuPressed()
{
    if (digitalRead(SNAKE_BTN_MENU) == LOW)
    {
        delay(40); // debounce
        if (digitalRead(SNAKE_BTN_MENU) == LOW)
        {
            // Wait for release
            while (digitalRead(SNAKE_BTN_MENU) == LOW) { delay(10); }
            return true;
        }
    }
    return false;
}

// =====================================================
// _readButtons() — buffer next direction (no 180°)
// =====================================================
void SnakeGame::_readButtons()
{
    if (digitalRead(SNAKE_BTN_UP) == LOW && _dirY != 1)
    {
        _nextDirX = 0; _nextDirY = -1;
    }
    else if (digitalRead(SNAKE_BTN_DOWN) == LOW && _dirY != -1)
    {
        _nextDirX = 0; _nextDirY = 1;
    }
    else if (digitalRead(SNAKE_BTN_LEFT) == LOW && _dirX != 1)
    {
        _nextDirX = -1; _nextDirY = 0;
    }
    else if (digitalRead(SNAKE_BTN_RIGHT) == LOW && _dirX != -1)
    {
        _nextDirX = 1; _nextDirY = 0;
    }
}

// =====================================================
// _resetGame() — fresh snake, new food, zero score
// =====================================================
void SnakeGame::_resetGame()
{
    _score   = 0;
    _len     = SNAKE_INITIAL_LENGTH;
    _dirX    = 1; _dirY    = 0;
    _nextDirX = 1; _nextDirY = 0;

    // Place snake horizontally in the centre
    int8_t sx = (int8_t)(MATRIXFORGE_GRID_WIDTH  / 2) - 1;
    int8_t sy = (int8_t)(MATRIXFORGE_GRID_HEIGHT / 2);
    for (int i = 0; i < _len; i++)
    {
        _snake[i].x = sx - (int8_t)i;
        _snake[i].y = sy;
    }

    _placeFood();
    _drawMatrix();
    _oledScore();
}

// =====================================================
// _tick() — advance game by one step
// =====================================================
void SnakeGame::_tick()
{
    // Commit buffered direction
    _dirX = _nextDirX;
    _dirY = _nextDirY;

    // New head position
    Point head = { (int8_t)(_snake[0].x + _dirX),
                   (int8_t)(_snake[0].y + _dirY) };

    // Wall collision
    if (head.x < 0 || head.x >= MATRIXFORGE_GRID_WIDTH ||
        head.y < 0 || head.y >= MATRIXFORGE_GRID_HEIGHT)
    {
        _flashDead();
        _beepDead();
        _oledGameOver();
        _state = GameState::DEAD;
        return;
    }

    // Self collision (ignore tail — it will vacate)
    if (_selfCollision(head))
    {
        _flashDead();
        _beepDead();
        _oledGameOver();
        _state = GameState::DEAD;
        return;
    }

    // Food eaten?
    bool ate = (head == _food);

    if (ate)
    {
        // Grow: insert new head without removing tail
        if (_len < SNAKE_MAX_LENGTH)
        {
            for (int i = _len; i > 0; i--)
                _snake[i] = _snake[i - 1];
            _snake[0] = head;
            _len++;
        }
        _score++;
        _beepEat();
        _placeFood();
        _oledScore();
    }
    else
    {
        // Normal move: slide body forward
        for (int i = _len - 1; i > 0; i--)
            _snake[i] = _snake[i - 1];
        _snake[0] = head;
    }

    _drawMatrix();
}

// =====================================================
// _selfCollision() — check if point hits body
//   Excludes the very last segment (it moves away)
// =====================================================
bool SnakeGame::_selfCollision(Point p) const
{
    for (int i = 0; i < _len - 1; i++)
        if (_snake[i] == p) return true;
    return false;
}

// =====================================================
// _placeFood() — random empty cell
// =====================================================
void SnakeGame::_placeFood()
{
    bool ok = false;
    while (!ok)
    {
        _food.x = (int8_t)random(0, MATRIXFORGE_GRID_WIDTH);
        _food.y = (int8_t)random(0, MATRIXFORGE_GRID_HEIGHT);
        ok = true;
        for (int i = 0; i < _len; i++)
            if (_snake[i] == _food) { ok = false; break; }
    }
}

// =====================================================
// _drawMatrix() — render frame to LED matrix
// =====================================================
void SnakeGame::_drawMatrix()
{
    _disp.clearDisplay();

    // Food — vivid orange
    _disp.drawPixel(_food.x, _food.y,
                    SNAKE_COL_FOOD_R,
                    SNAKE_COL_FOOD_G,
                    SNAKE_COL_FOOD_B);

    // Body — gradient from bright (near head) to dim (tail)
    for (int i = _len - 1; i >= 1; i--)
    {
        uint8_t brightness = (uint8_t)map(i, _len - 1, 1,
                                          SNAKE_BODY_DIM,
                                          SNAKE_BODY_BRIGHT);
        uint8_t tint = brightness / 6; // slight blue-green tint
        _disp.drawPixel(_snake[i].x, _snake[i].y,
                        0, brightness, tint);
    }

    // Head — maximum brightness
    _disp.drawPixel(_snake[0].x, _snake[0].y,
                    SNAKE_COL_HEAD_R,
                    SNAKE_COL_HEAD_G,
                    SNAKE_COL_HEAD_B);

    _disp.show();
}

// =====================================================
// _drawTitleMatrix() — splash on LED matrix
// =====================================================
void SnakeGame::_drawTitleMatrix()
{
    _disp.clearDisplay();
    _disp.setFgColor(0, 200, 50);
    _disp.drawText(0, 5, "SNAKE", true);
    _disp.show();
}

// =====================================================
// _flashDead() — red flash animation on death
// =====================================================
void SnakeGame::_flashDead()
{
    for (uint8_t f = 0; f < 3; f++)
    {
        // Full red wash
        _disp.fillDisplay(80, 0, 0);
        _disp.show();
        delay(130);

        // Snake outline in bright red
        _disp.clearDisplay();
        for (int i = 0; i < _len; i++)
            _disp.drawPixel(_snake[i].x, _snake[i].y, 255, 0, 0);
        _disp.show();
        delay(130);
    }
    _disp.clearDisplay();
    _disp.show();
}

// =====================================================
// OLED screens
// =====================================================
void SnakeGame::_oledTitle()
{
    _oled.clearDisplay();
    _oled.setTextColor(SH110X_WHITE);

    _oled.setTextSize(2);
    _oled.setCursor(16, 6);
    _oled.println("  SNAKE");

    _oled.drawLine(0, 26, 127, 26, SH110X_WHITE);

    _oled.setTextSize(1);
    _oled.setCursor(14, 34);
    _oled.println("Press MENU to start");
    _oled.setCursor(10, 48);
    _oled.println("D-PAD to steer snake");

    _oled.display();
}

void SnakeGame::_oledScore()
{
    _oled.clearDisplay();
    _oled.setTextColor(SH110X_WHITE);

    _oled.setTextSize(1);
    _oled.setCursor(28, 4);
    _oled.println("MATRIXFORGE SNAKE");
    _oled.drawLine(0, 14, 127, 14, SH110X_WHITE);

    _oled.setTextSize(3);
    // Right-align score
    int digits = (_score == 0) ? 1 : (int)floor(log10(_score)) + 1;
    int16_t sx = (128 - digits * 18) / 2;
    _oled.setCursor(sx, 22);
    _oled.println(_score);

    _oled.setTextSize(1);
    _oled.setCursor(46, 56);
    _oled.println("SCORE");

    _oled.display();
}

void SnakeGame::_oledGameOver()
{
    _oled.clearDisplay();
    _oled.setTextColor(SH110X_WHITE);

    _oled.setTextSize(2);
    _oled.setCursor(10, 4);
    _oled.println("GAME OVER");

    _oled.drawLine(0, 24, 127, 24, SH110X_WHITE);

    _oled.setTextSize(1);
    _oled.setCursor(26, 32);
    _oled.print("Your score: ");
    _oled.println(_score);

    _oled.setCursor(12, 48);
    _oled.println("MENU = Play again");

    _oled.display();
}

// =====================================================
// Buzzer sounds
// =====================================================
void SnakeGame::_beepEat()
{
    tone(SNAKE_BUZZER_PIN, 880,  70); delay(80);
    tone(SNAKE_BUZZER_PIN, 1200, 60); delay(70);
    noTone(SNAKE_BUZZER_PIN);
}

void SnakeGame::_beepDead()
{
    tone(SNAKE_BUZZER_PIN, 400, 150); delay(160);
    tone(SNAKE_BUZZER_PIN, 300, 150); delay(160);
    tone(SNAKE_BUZZER_PIN, 200, 300); delay(320);
    noTone(SNAKE_BUZZER_PIN);
}

void SnakeGame::_beepStart()
{
    tone(SNAKE_BUZZER_PIN, 600,  80); delay(90);
    tone(SNAKE_BUZZER_PIN, 900,  80); delay(90);
    tone(SNAKE_BUZZER_PIN, 1200, 120); delay(130);
    noTone(SNAKE_BUZZER_PIN);
}
