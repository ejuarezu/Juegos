#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define UP_BUTTON D1
#define DOWN_BUTTON D2
#define BUZZER D3

const unsigned long PADDLE_RATE = 64;
const unsigned long BALL_RATE = 16;
const uint8_t PADDLE_HEIGHT = 12;
const uint8_t SCORE_LIMIT = 9;

Adafruit_SSD1306 display(128, 64, &Wire);

bool game_over, win;

uint8_t player_score, mcu_score;
uint8_t ball_x = 53, ball_y = 26;
uint8_t ball_dir_x = 1, ball_dir_y = 1;

unsigned long ball_update;
unsigned long paddle_update;

const uint8_t MCU_X = 12;
uint8_t mcu_y = 16;

const uint8_t PLAYER_X = 115;
uint8_t player_y = 16;

void setup() {
    pinMode(UP_BUTTON, INPUT_PULLUP);
    pinMode(DOWN_BUTTON, INPUT_PULLUP);
    pinMode(BUZZER, OUTPUT);

    display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
    display.clearDisplay();
    drawCourt();
    display.display();

    ball_update = millis();
    paddle_update = ball_update;
}

void loop() {
    bool update_needed = false;
    unsigned long time = millis();

    static bool up_state = false;
    static bool down_state = false;
    
    up_state |= (digitalRead(UP_BUTTON) == LOW);
    down_state |= (digitalRead(DOWN_BUTTON) == LOW);

    if (time > ball_update) {
        uint8_t new_x = ball_x + ball_dir_x;
        uint8_t new_y = ball_y + ball_dir_y;

        // Rebotar en las paredes laterales
        if (new_x == 0 || new_x == 127) {
            ball_dir_x = -ball_dir_x;
            new_x += ball_dir_x + ball_dir_x;

            if (new_x < 64) {
                player_scoreTone();
                player_score++;
            } else {
                mcu_scoreTone();
                mcu_score++;
            }

            if (player_score == SCORE_LIMIT || mcu_score == SCORE_LIMIT) {
                win = player_score > mcu_score;
                game_over = true;
            }
        }

        // Rebotar en las paredes superior e inferior
        if (new_y == 0 || new_y == 53) {
            wallTone();
            ball_dir_y = -ball_dir_y;
            new_y += ball_dir_y + ball_dir_y;
        }

        // Rebotar en la paleta de la CPU
        if (new_x == MCU_X && new_y >= mcu_y && new_y <= mcu_y + PADDLE_HEIGHT) {
            mcuPaddleTone();
            ball_dir_x = -ball_dir_x;
            new_x += ball_dir_x + ball_dir_x;
        }

        // Rebotar en la paleta del jugador
        if (new_x == PLAYER_X && new_y >= player_y && new_y <= player_y + PADDLE_HEIGHT) {
            playerPaddleTone();
            ball_dir_x = -ball_dir_x;
            new_x += ball_dir_x + ball_dir_x;
        }

        display.drawPixel(ball_x, ball_y, BLACK);
        display.drawPixel(new_x, new_y, WHITE);
        ball_x = new_x;
        ball_y = new_y;

        ball_update += BALL_RATE;
        update_needed = true;
    }

    if (time > paddle_update) {
        paddle_update += PADDLE_RATE;

        // CPU paddle
        display.drawFastVLine(MCU_X, mcu_y, PADDLE_HEIGHT, BLACK);
        const uint8_t half_paddle = PADDLE_HEIGHT >> 1;

        if (mcu_y + half_paddle > ball_y) mcu_y--;
        if (mcu_y + half_paddle < ball_y) mcu_y++;

        if (mcu_y < 1) mcu_y = 1;
        if (mcu_y + PADDLE_HEIGHT > 53) mcu_y = 53 - PADDLE_HEIGHT;

        // Player paddle
        display.drawFastVLine(MCU_X, mcu_y, PADDLE_HEIGHT, WHITE);
        display.drawFastVLine(PLAYER_X, player_y, PADDLE_HEIGHT, BLACK);

        if (up_state) player_y--;
        if (down_state) player_y++;

        up_state = down_state = false;

        if (player_y < 1) player_y = 1;
        if (player_y + PADDLE_HEIGHT > 53) player_y = 53 - PADDLE_HEIGHT;

        display.drawFastVLine(PLAYER_X, player_y, PADDLE_HEIGHT, WHITE);
        update_needed = true;
    }

    if (update_needed) {
        if (game_over) {
            display.clearDisplay();
            display.setCursor(40, 28);
            display.print(win ? "YOU WIN!!" : "YOU LOSE!");
            display.display();

            delay(5000);

            // Reiniciar juego
            display.clearDisplay();
            ball_x = 53;
            ball_y = 26;
            ball_dir_x = 1;
            ball_dir_y = 1;
            mcu_y = 16;
            player_y = 16;
            mcu_score = 0;
            player_score = 0;
            game_over = false;
            drawCourt();
        }

        display.setTextColor(WHITE, BLACK);
        display.setCursor(0, 56);
        display.print(mcu_score);
        display.setCursor(122, 56);
        display.print(player_score);
        display.display();
    }
}

// Funciones de sonido adaptadas para buzzer pasivo en ESP8266
void beep(int frequency, int duration) {
    analogWrite(BUZZER, 512);
    delayMicroseconds(1000000 / frequency);
    analogWrite(BUZZER, 0);
    delay(duration);
}

void playerPaddleTone() { beep(250, 25); }
void mcuPaddleTone() { beep(225, 25); }
void wallTone() { beep(200, 25); }
void player_scoreTone() { beep(200, 25); delay(50); beep(250, 25); }
void mcu_scoreTone() { beep(250, 25); delay(25); beep(200, 25); }

void drawCourt() {
    display.drawRect(0, 0, 128, 54, WHITE);
}
