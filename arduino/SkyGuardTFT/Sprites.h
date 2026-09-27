// Pixel-art sprites. Each letter is one pixel; '.' is see-through.
// Colors for each letter are in spriteColor() in SkyGuardTFT.ino.
#pragma once

#define EAGLE_BODY_W 22
#define EAGLE_BODY_H 18
const char *const EAGLE_BODY[] = {
  "......................",
  "......................",
  "......................",
  "......................",
  "..............KKKK....",
  ".............KWWWWK...",
  "............KWWWWEWK..",
  "...........KGWWWWWWYK.",
  "KKK.......KBGWWWWWKYYK",
  "KWWKK...KKBBGGWWKKYOK.",
  "KGWWWKKKBBBBBBGGK.KK..",
  ".KGWWWBBBBBBBBBBBK....",
  "..KGGWBBBBBBBBBBBK....",
  "...KKKDDBBBBBBBDK.....",
  ".....KKDDDDDDDDK......",
  ".......KKKKKKKK.......",
  "........OY..OY........",
  "......................",
};

#define EAGLE_WING_UP_W 22
#define EAGLE_WING_UP_H 18
const char *const EAGLE_WING_UP[] = {
  "..KK..................",
  "..KDK.................",
  "..KLDK................",
  "...KLDKK..............",
  "...KLLDDK.............",
  "....KLLDDKK...........",
  "....KLLLDDDK..........",
  ".....KLLLDDBK.........",
  ".....KKLLLDBBK........",
  "......KKKLLBBK........",
  "........KKKKK.........",
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
};

#define EAGLE_WING_MID_W 22
#define EAGLE_WING_MID_H 18
const char *const EAGLE_WING_MID[] = {
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "...KKKKKKKK...........",
  ".KKLLLDDDDBKK.........",
  "KLLLLDDDDDDBBK........",
  ".KKKKLLLDDDBK.........",
  ".....KKKKKKK..........",
  "......................",
  "......................",
  "......................",
  "......................",
};

#define EAGLE_WING_DOWN_W 22
#define EAGLE_WING_DOWN_H 18
const char *const EAGLE_WING_DOWN[] = {
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "........KKKKK.........",
  "......KKLLDBBK........",
  ".....KLLLDDDBK........",
  "....KLLLDDDDK.........",
  "...KLLLDDDKK..........",
  "...KLLDDKK............",
  "..KLDDKK..............",
  "..KDKK................",
  "..KK..................",
};

#define EAGLE_TALONS_W 22
#define EAGLE_TALONS_H 18
const char *const EAGLE_TALONS[] = {
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "......................",
  "........OY...OY.......",
  ".......OYY..OYY.......",
  "......Y.Y.YY.Y.Y......",
};

#define BUG_BODY_W 11
#define BUG_BODY_H 10
const char *const BUG_BODY[] = {
  "...........",
  "...........",
  "...........",
  "..KK.KKKK..",
  ".KMPKPSPSK.",
  "KEPPKQSQSQK",
  "KPPPKPSPSK.",
  ".KQQKQQQK..",
  "..KKNKKNK..",
  "....N..N...",
};

#define BUG_WING_A_W 11
#define BUG_WING_A_H 10
const char *const BUG_WING_A[] = {
  ".....KK....",
  "....KCCK...",
  "...KCcCK...",
  "....KKK....",
  "...........",
  "...........",
  "...........",
  "...........",
  "...........",
  "...........",
};

#define BUG_WING_B_W 11
#define BUG_WING_B_H 10
const char *const BUG_WING_B[] = {
  "...........",
  "...........",
  "......KKK..",
  "....KKCCcK.",
  "....KCCKK..",
  "...........",
  "...........",
  "...........",
  "...........",
  "...........",
};

#define BEETLE_A_W 18
#define BEETLE_A_H 12
const char *const BEETLE_A[] = {
  "..N.....KKKKK.....",
  "...N..KKRRRRRKK...",
  "....NKRRwRRRRRRK..",
  "...KKRRwRRNRRRRRK.",
  "..KNNKRRRRRRRRNRK.",
  ".KNENKRNRRRRRRRRRK",
  ".KNNNKRRRRRNRRRRRK",
  "..KNNKrRRRRRRRRRrK",
  "...KKKrrRRRRRRRrK.",
  "......KKrrrrrrrK..",
  ".....N.KKKKKKKK...",
  "....N..N...N..N...",
};

#define BEETLE_B_W 18
#define BEETLE_B_H 12
const char *const BEETLE_B[] = {
  "..N.....KKKKK.....",
  "...N..KKRRRRRKK...",
  "....NKRRwRRRRRRK..",
  "...KKRRwRRNRRRRRK.",
  "..KNNKRRRRRRRRNRK.",
  ".KNENKRNRRRRRRRRRK",
  ".KNNNKRRRRRNRRRRRK",
  "..KNNKrRRRRRRRRRrK",
  "...KKKrrRRRRRRRrK.",
  "......KKrrrrrrrK..",
  "......NKKKKKKKKN..",
  ".......N..N..N....",
};

#define FISH_A_W 16
#define FISH_A_H 8
const char *const FISH_A[] = {
  ".....KKKK.......",
  "...KKFHHFKK..KK.",
  "..KFHHFFFFfK.KFK",
  ".KwEFFFFFFFfKFfK",
  ".KFFFFFFFFFffFfK",
  "..KfFFFFFFffKKfK",
  "...KKfffffKK..KK",
  ".....KKKKK......",
};

#define FISH_B_W 16
#define FISH_B_H 8
const char *const FISH_B[] = {
  ".....KKKK.......",
  "...KKFHHFKK.....",
  "..KFHHFFFFfKKKK.",
  ".KwEFFFFFFFfFffK",
  ".KFFFFFFFFFffFfK",
  "..KfFFFFFFffKKKK",
  "...KKfffffKK....",
  ".....KKKKK......",
};
