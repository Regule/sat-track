#include "DateTime.h"
#include <iostream>
#include <sstream>
#include <iomanip>

DateTime::DateTime()
    : year(0), month(0), day(0), hour(0), minute(0), second(0) {}

DateTime::DateTime(const std::string& dateTimeString) {
    std::istringstream iss(dateTimeString);
    char separator;
    iss >> year >> separator >> month >> separator >> day >> separator >>
        hour >> separator >> minute >> separator >> second;
}

std::string DateTime::ToUtcTimeString() const {
    std::ostringstream oss;
    oss << std::setfill('0');
    oss << std::setw(4) << year << '-';
    oss << std::setw(2) << month << '-';
    oss << std::setw(2) << day << ' ';
    oss << std::setw(2) << hour << ':';
    oss << std::setw(2) << minute << ':';
    oss << std::setw(2) << second;
    return oss.str();
}

void DateTime::AddSeconds(int seconds) {
    second += seconds;
    AdjustDateTime();
}

bool DateTime::operator<=(const DateTime& other) const {
    if (year < other.year)
        return true;
    if (year > other.year)
        return false;
    if (month < other.month)
        return true;
    if (month > other.month)
        return false;
    if (day < other.day)
        return true;
    if (day > other.day)
        return false;
    if (hour < other.hour)
        return true;
    if (hour > other.hour)
        return false;
    if (minute < other.minute)
        return true;
    if (minute > other.minute)
        return false;
    return second <= other.second;
}

void DateTime::AdjustDateTime() {
    if (second >= 60) {
        int minutesToAdd = second / 60;
        second %= 60;
        minute += minutesToAdd;
    }
    if (minute >= 60) {
        int hoursToAdd = minute / 60;
        minute %= 60;
        hour += hoursToAdd;
    }
    if (hour >= 24) {
        int daysToAdd = hour / 24;
        hour %= 24;
        day += daysToAdd;
    }
    // Handle month/year adjustment if necessary
    // (code omitted for brevity)
}

