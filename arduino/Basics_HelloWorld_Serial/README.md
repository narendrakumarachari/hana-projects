# Basics_HelloWorld_Serial

> Prints `Hello World` to the Serial Monitor every 5 seconds. The "is my board alive?" test.

| | |
|---|---|
| **Old name** | `HelloWorld` |
| **Board** | Any Arduino (Uno used) |
| **Libraries** | none |
| **Last edited** | 2026-09-26 |

## What it does
Opens the serial port at **9600 baud**, waits until the port is connected (this only matters on boards with native USB, such as the Leonardo), then prints `Hello World` every 5 seconds.

## Parts
- An Arduino and a USB cable. Nothing else.

## How to use
1. Upload.
2. Open **Tools → Serial Monitor** at **9600 baud**.
3. `Hello World` appears every 5 s.

## Code review notes
- Nothing to fix. It is only a test.

## To-do
- [ ] Nothing required. Use it as the first upload when testing a new board or USB cable.

## Libraries to install

**Headers included:** none

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
