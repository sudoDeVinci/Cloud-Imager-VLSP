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
#define CERT_DIR "//certs"
#define AP_DIR "//aps"
#define LOG_DIR "//logs"

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
void writeToFile(fs::FS& fs, const String& filename, const String& message);

std::vector<String*> readFile(fs::FS &fs, const char * path);

#endif