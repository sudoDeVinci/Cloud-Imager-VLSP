#pragma once
#ifndef FILEIO_H
#define FILEIO_H

#include "Arduino.h"
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
#define CERT_FOLDER "/certs"
#define SERVER_FOLDER "/servers"
#define AP_FOLDER "/aps"
#define PROFILE_FOLDER "/profiles"
void sdmmcInit(void); 

void listDir(fs::FS &fs, const char * dirname, uint8_t levels);
void createDir(fs::FS &fs, const char * path);
void removeDir(fs::FS &fs, const char * path);
void readFile(fs::FS &fs, const char * path);
void writeFile(fs::FS &fs, const char * path, const char * message);
void appendFile(fs::FS &fs, const char * path, const char * message);
void renameFile(fs::FS &fs, const char * path1, const char * path2);
void deleteFile(fs::FS &fs, const char * path);
void testFileIO(fs::FS &fs, const char * path);

void writejpg(fs::FS &fs, const char * path, const uint8_t *buf, size_t size);
int readFileNum(fs::FS &fs, const char * dirname);
const char* readString(const String& line);
#endif