#pragma once
#ifndef IO_H
#define IO_H

#include <Arduino.h>
#include <vector>
#include "FS.h"
#include "SD_MMC.h"

#define DEBUG 1

#if DEBUG == 1
#define debug(...) Serial.print(__VA_ARGS__)
#define debugln(...) Serial.println(__VA_ARGS__)
#define debugf(...) Serial.printf(__VA_ARGS__)
#else
#define debug(...)
#define debugln(...)
#define debugf(...)
#endif

#define SD_MMC_CMD  38 //Please do not modify it.
#define SD_MMC_CLK  39 //Please do not modify it. 
#define SD_MMC_D0   40 //Please do not modify it.

#define LOG_FILE "/readings.csv"

/**
 * Initialize the sdcard file system. 
 */
void sdmmcInit(void);

/**
 * Extract the double-quote enclosed string from a line in a conf file.
 */
const char* readString(const String& line);

/**
 * Attempt to append to a given file.
 * Create the file if it doesn't exist.
 */
void writeToCSV(fs::FS& fs, const String& filename, const String& message);

/**
 * Read the csv of past readings and return a vector of String arrays.
 */
std::vector<String*> readCSV(fs::FS &fs, const char* path);

/**
 * Write an image buffer into a jpg file. 
 */
void writejpg(fs::FS &fs, const char* path, const uint8_t* buf, size_t size);

/**
 * Read an image buffer from a jpg file. 
 */
uint8_t* readjpg(fs::FS &fs, const char* path);

#endif