#ifndef DATETIME_H
#define DATETIME_H

#include <iostream>
#include <sstream>
#include <iomanip>


class DateTime{
public:
  DateTime();
  DateTime(const std::string& dateTimeString);
private:
  unsigned int year;
  unsigned int month;
  unsigned int day;
  unsigned int hour;
  unsigned int minute;
  unsigned int second;
};

#endif
