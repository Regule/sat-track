#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include "SGP4/SGP4.h"

struct GroundTraceEntry {
    double latitude;
    double longitude;
    std::string timestamp;
};

std::vector<GroundTraceEntry> predictGroundTrace(const std::string& tleFile, const std::string& startTime, const std::string& endTime) {
    std::vector<GroundTraceEntry> groundTrace;
    std::ifstream file(tleFile);
    if (!file.is_open()) {
        std::cout << "Error opening TLE file: " << tleFile << std::endl;
        return groundTrace;
    }

    std::string line1, line2;
    std::getline(file, line1);
    std::getline(file, line2);
    file.close();

    std::istringstream tleStream(line1 + '\n' + line2 + '\n');
    Satellite satellite(tleStream);

    DateTime startDateTime(startTime);
    DateTime endDateTime(endTime);

    while (startDateTime <= endDateTime) {
        ECI position = satellite.FindPosition(startDateTime);
        Geodetic observerPosition = position.ToGeodetic();

        GroundTraceEntry entry;
        entry.latitude = observerPosition.latitude;
        entry.longitude = observerPosition.longitude;
        entry.timestamp = startDateTime.ToUtcTimeString();
        groundTrace.push_back(entry);

        startDateTime.AddSeconds(60);  // Predict position every minute
    }

    return groundTrace;
}

int main() {
    std::string tleFile = "satellite.tle";
    std::string startTime = "2023-07-06 00:00:00";  // Specify the start time in UTC
    std::string endTime = "2023-07-06 23:59:59";    // Specify the end time in UTC

    std::vector<GroundTraceEntry> groundTrace = predictGroundTrace(tleFile, startTime, endTime);

    for (const auto& entry : groundTrace) {
        std::cout << "Timestamp: " << entry.timestamp << std::endl;
        std::cout << "Latitude: " << entry.latitude << std::endl;
        std::cout << "Longitude: " << entry.longitude << std::endl;
        std::cout << std::endl;
    }

    return 0;
}
