#include "fileio.h"


void sdmmcInit(void){
  SD_MMC.setPins(SD_MMC_CLK, SD_MMC_CMD, SD_MMC_D0);
  if (!SD_MMC.begin("/sdcard", true, true, SDMMC_FREQ_DEFAULT, 5)) {
    debugln("Card Mount Failed");
    return;
  }
  uint8_t cardType = SD_MMC.cardType();
  if(cardType == CARD_NONE){
      debugln("No SD_MMC card attached");
      return;
  }

  uint64_t cardSize = SD_MMC.cardSize() / (1024 * 1024);
  debugf("SD_MMC Card Size: %lluMB\n", cardSize);  
  debugf("Total space: %lluMB\r\n", SD_MMC.totalBytes() / (1024 * 1024));
  debugf("Used space: %lluMB\r\n", SD_MMC.usedBytes() / (1024 * 1024));
}

void listDir(fs::FS &fs, const char * dirname, uint8_t levels){
    debugf("Listing directory: %s\n", dirname);

    File root = fs.open(dirname);
    if(!root){
        debugln("Failed to open directory");
        return;
    }
    if(!root.isDirectory()){
        debugln("Not a directory");
        return;
    }

    File file = root.openNextFile();
    while(file){
        if(file.isDirectory()){
            debug("  DIR : ");
            debugln(file.name());
            if(levels){
                listDir(fs, file.path(), levels -1);
            }
        } else {
            debug("  FILE: ");
            debug(file.name());
            debug("  SIZE: ");
            debugln(file.size());
        }
        file = root.openNextFile();
    }
}

void createDir(fs::FS &fs, const char * path){
    debugf("Creating Dir: %s\n", path);
    if(fs.mkdir(path)){
        debugln("Dir created");
    } else {
        debugln("mkdir failed");
    }
}

void removeDir(fs::FS &fs, const char * path){
    debugf("Removing Dir: %s\n", path);
    if(fs.rmdir(path)){
        debugln("Dir removed");
    } else {
        debugln("rmdir failed");
    }
}

void readFile(fs::FS &fs, const char * path){
    debugf("Reading file: %s\n", path);

    File file = fs.open(path);
    if(!file){
        debugln("Failed to open file for reading");
        return;
    }

    debug("Read from file: ");
    while(file.available()){
        Serial.write(file.read());
    }
}

void writeFile(fs::FS &fs, const char * path, const char * message){
    debugf("Writing file: %s\n", path);

    File file = fs.open(path, FILE_WRITE);
    if(!file){
        debugln("Failed to open file for writing");
        return;
    }
    if(file.print(message)){
        debugln("File written");
    } else {
        debugln("Write failed");
    }
}

void appendFile(fs::FS &fs, const char * path, const char * message){
    debugf("Appending to file: %s\n", path);

    File file = fs.open(path, FILE_APPEND);
    if(!file){
        debugln("Failed to open file for appending");
        return;
    }
    if(file.print(message)){
        debugln("Message appended");
    } else {
        debugln("Append failed");
    }
}

void renameFile(fs::FS &fs, const char * path1, const char * path2){
    debugf("Renaming file %s to %s\n", path1, path2);
    if (fs.rename(path1, path2)) {
        debugln("File renamed");
    } else {
        debugln("Rename failed");
    }
}

void deleteFile(fs::FS &fs, const char * path){
    debugf("Deleting file: %s\n", path);
    if(fs.remove(path)){
        debugln("File deleted");
    } else {
        debugln("Delete failed");
    }
}

void testFileIO(fs::FS &fs, const char * path){
    File file = fs.open(path);
    static uint8_t buf[512];
    size_t len = 0;
    uint32_t start = millis();
    uint32_t end = start;
    if(file){
        len = file.size();
        size_t flen = len;
        start = millis();
        while(len){
            size_t toRead = len;
            if(toRead > 512){
                toRead = 512;
            }
            file.read(buf, toRead);
            len -= toRead;
        }
        end = millis() - start;
        debugf("%u bytes read for %u ms\r\n", flen, end);
        file.close();
    } else {
        debugln("Failed to open file for reading");
    }

    file = fs.open(path, FILE_WRITE);
    if(!file){
        debugln("Failed to open file for writing");
        return;
    }

    size_t i;
    start = millis();
    for(i=0; i<2048; i++){
        file.write(buf, 512);
    }
    end = millis() - start;
    debugf("%u bytes written for %u ms\n", 2048 * 512, end);
    file.close();
}

void writejpg(fs::FS &fs, const char * path, const uint8_t *buf, size_t size){
    File file = fs.open(path, FILE_WRITE);
    if(!file){
      debugln("Failed to open file for writing");
      return;
    }
    file.write(buf, size);
    debugf("Saved file to path: %s\r\n", path);
}

int readFileNum(fs::FS &fs, const char * dirname){
    File root = fs.open(dirname);
    if(!root){
        debugln("Failed to open directory");
        return -1;
    }
    if(!root.isDirectory()){
        debugln("Not a directory");
        return -1;
    }

    File file = root.openNextFile();
    int num=0;
    while(file){
      file = root.openNextFile();
      num++;
    }
    return num;  
}

/**
 * Extract the double-quote enclosed string from a line in a conf file.
 */
const char* readString(const String& line) {
    // Find the position of '=' and the first double quote
    int equalsIndex = line.indexOf('=');
    int quoteStartIndex = line.indexOf('"', equalsIndex);

    // Check if '=' and '"' are found
    if (equalsIndex != -1 && quoteStartIndex != -1) {
        int quoteEndIndex = line.indexOf('"', quoteStartIndex + 1);

        // Check if the second double quote is found
        if (quoteEndIndex != -1) {
            int pathStartIndex = quoteStartIndex + 1;
            int pathLength = quoteEndIndex - pathStartIndex;

            // Extract the file path
            char* filePath = new char[pathLength + 1];  // +1 for null-terminator
            line.substring(pathStartIndex, quoteEndIndex).toCharArray(filePath, pathLength + 1);

            return filePath;
        }
    }

    return nullptr;
}