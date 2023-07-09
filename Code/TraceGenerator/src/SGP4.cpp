#include "SGP4.h"
#include <stdexcept>
#include <sstream>
#include <iomanip>

Satellite::Satellite(std::istream& tleStream) {
    std::string line1, line2;
    std::getline(tleStream, line1);
    std::getline(tleStream, line2);
    if (line1.empty() || line2.empty()) {
        throw std::invalid_argument("Invalid TLE data.");
    }

    std::istringstream iss1(line1);
    std::istringstream iss2(line2);

    // Line 1
    std::string satName;
    iss1.ignore(2); // Ignore line number
    std::getline(iss1, satName, ' ');
    std::getline(iss1, satName, '\r');
    satName_ = satName;

    // Line 2
    std::string intlDesignator, epochYear, epochDay, meanMotionDt2, meanMotionDt6, bstarTerm, elementSetNumber;
    iss2.ignore(2); // Ignore line number
    std::getline(iss2, intlDesignator, ' ');
    iss2.ignore(2); // Ignore security classification and international designator launch year
    std::getline(iss2, epochYear, ' ');
    std::getline(iss2, epochDay, ' ');
    std::getline(iss2, meanMotionDt2, ' ');
    std::getline(iss2, meanMotionDt6, ' ');
    std::getline(iss2, bstarTerm, ' ');
    std::getline(iss2, elementSetNumber, ' ');

    std::istringstream(epochYear) >> epochYear_;
    std::istringstream(epochDay) >> epochDay_;
    std::istringstream(meanMotionDt2) >> meanMotionDt2_;
    std::istringstream(meanMotionDt6) >> meanMotionDt6_;
    std::istringstream(bstarTerm) >> bstarTerm_;
    std::istringstream(elementSetNumber) >> elementSetNumber_;
}

ECI Satellite::FindPosition(const DateTime& dateTime) const {
    double tsince = (dateTime.JulianDate() - epochJulianDate()) * kMinutesPerDay;
    return sgp4_->FindPosition(tsince);
}

double Satellite::epochJulianDate() const {
    return epochYear_ + epochDay_;
}

DateTime::DateTime(const std::string& dateTimeString) {
    std::istringstream iss(dateTimeString);
    char separator;
    iss >> year >> separator >> month >> separator >> day >> separator >>
        hour >> separator >> minute >> separator >> second;
}

double DateTime::JulianDate() const {
    int a = (14 - month) / 12;
    int y = year + 4800 - a;
    int m = month + 12 * a - 3;
    double jd = day + (153 * m + 2) / 5 + 365 * y + y / 4 - y / 100 + y / 400 - 32045;
    jd += (hour - 12) / 24.0 + minute / 1440.0 + second / 86400.0;
    return jd;
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

