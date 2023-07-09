#include "ECI.h"
#include <cmath>

ECI::ECI(double x, double y, double z)
    : x(x), y(y), z(z) {}

Geodetic ECI::ToGeodetic() const {
    const double a = 6378.137;           // Semi-major axis of the Earth (in km)
    const double f = 1 / 298.257223563;  // Flattening factor
    const double b = a * (1 - f);        // Semi-minor axis of the Earth (in km)
    const double eSquared = (a * a - b * b) / (a * a);  // Eccentricity squared

    double longitude = std::atan2(y, x);
    double p = std::sqrt(x * x + y * y);
    double latitude = std::atan2(z, p);

    double sinLatitude = std::sin(latitude);
    double cosLatitude = std::cos(latitude);
    double N = a / std::sqrt(1 - eSquared * sinLatitude * sinLatitude);

    double altitude = p / cosLatitude - N;

    Geodetic result;
    result.latitude = latitude * 180 / M_PI;     // Convert latitude to degrees
    result.longitude = longitude * 180 / M_PI;   // Convert longitude to degrees
    result.altitude = altitude;                  // Altitude in km

    return result;
}

