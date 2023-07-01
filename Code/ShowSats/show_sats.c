#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <GL/glut.h>

#define PI 3.14159265358979323846
#define MAX_SATELLITE_COUNT 10000

typedef struct {
    double x;
    double y;
    double z;
} Point3D;

typedef struct {
    double lat;
    double lon;
    double alt;
} Satellite;

Satellite satellites[MAX_SATELLITE_COUNT];
int satelliteCount = 0;

void loadTLEData(const char* filename) {
    FILE* file = fopen(filename, "r");
    if (file == NULL) {
        printf("Error opening TLE file.\n");
        exit(1);
    }

    char line1[69];
    char line2[69];
    while (fgets(line1, sizeof(line1), file) && fgets(line2, sizeof(line2), file)) {
        line1[68] = '\0';
        line2[68] = '\0';

        sscanf(line1 + 19, "%lf", &satellites[satelliteCount].lat);
        sscanf(line2 + 19, "%lf", &satellites[satelliteCount].lon);
        sscanf(line2 + 33, "%lf", &satellites[satelliteCount].alt);

        satelliteCount++;
        if(satelliteCount >= MAX_SATELLITE_COUNT){
          break;
        }
    }
    fclose(file);
}

Point3D toCartesian(double lat, double lon, double alt) {
    double latRad = lat * PI / 180.0;
    double lonRad = lon * PI / 180.0;
    double radius = alt + 1.0;

    Point3D point;
    point.x = radius * cos(latRad) * cos(lonRad);
    point.y = radius * sin(latRad);
    point.z = radius * cos(latRad) * sin(lonRad);

    return point;
}

void drawSatellites() {
    for (int i = 0; i < satelliteCount; i++) {
        Point3D point = toCartesian(satellites[i].lat, satellites[i].lon, satellites[i].alt);
        glPushMatrix();
        glColor3f(1.0f, 0.0f, 0.0f);
        glTranslatef(point.x, point.y, point.z);
        glutSolidSphere(0.01, 10, 10);
        glPopMatrix();
    }
}

void display() {
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glLoadIdentity();
    gluLookAt(0.0, 1.0, 2.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0);

    glColor3f(0.0f, 0.0f, 1.0f);
    glutWireSphere(1.0, 20, 20);

    drawSatellites();

    glutSwapBuffers();
}

void reshape(int width, int height) {
    glViewport(0, 0, width, height);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluPerspective(45.0, (double)width / (double)height, 1.0, 10.0);
    glMatrixMode(GL_MODELVIEW);
}

int main(int argc, char** argv) {
    if (argc < 2) {
        printf("Usage: %s <TLE filename>\n", argv[0]);
        return 1;
    }

    loadTLEData(argv[1]);

    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
    glutInitWindowSize(800, 600);
    glutCreateWindow("Satellites Over World");
    glEnable(GL_DEPTH_TEST);
    glutDisplayFunc(display);
    glutReshapeFunc(reshape);
    glutMainLoop();

    return 0;
}

