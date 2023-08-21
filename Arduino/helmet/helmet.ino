#include <Servo.h>
#include <SoftwareSerial.h>

#define PIN_POMPA 6 //pompa na pinie 6
#define PIN_ODPOWIETRZANIE 7 //odpowietrzenie na pinie 7
#define PIN_SERWO 8 //serwo na pinie 8
#define CZAS_AKTYWACJA_SERWA 120000 //czas przez który serwo wychylone 2 min
#define CZAS_DZIALANIA_POMPY 300000 //czas działania pompy 5 min
#define CZAS_OPOZNIENIA 900000 //przerwa pomiedzy dzialaniem 15 min
#define SERWO_POZYCJA_SPOCZYNKOWA 25 //pozycja "0" serwa
#define SERWO_POZYCJA_AKTYWNA 120 //pozycja wychylonego serwa
#define CZAS_OD_WLACZENIA 10000 //czas przed startem dzialania - 10s

#define SOFTWARE_SERIAL_RX 1
#define SOFTWARE_SERIAL_TX 2
#define SOFTWAR_SERIAL_READ_TIMEOUT 10
#define ROZKAZ_POMPA_WLACZ 'P'
#define ROZKAZ_POMPA_WYLACZ 'L'
#define ROZKAZ_ODPOWIETRZANIE_WLACZ 'O'
#define ROZKAZ_SERWO_WLACZ 'S'
#define ROZKAZ_SERWO_WYLACZ 'Z'
#define ROZKAZ_BRAK_ROZKAZU 'N'


Servo serwo;
SoftwareSerial command_serial(SOFTWARE_SERIAL_RX, SOFTWARE_SERIAL_TX);

void enable_pump(){ //wlaczenie pompy,zamkniecie zaworu
  digitalWrite(PIN_POMPA, HIGH);
  digitalWrite(PIN_ODPOWIETRZANIE, HIGH);
}

void release_pump(){ //zatrzymanie pompy, odpowietrzenie
  digitalWrite(PIN_POMPA, LOW);
  digitalWrite(PIN_ODPOWIETRZANIE, LOW);
}

void halt_pump(){ //zatrzymanie pompy, zawór zamknięty 
  digitalWrite(PIN_POMPA, LOW);
  digitalWrite(PIN_ODPOWIETRZANIE, HIGH);
}

void setup() { //ustawienia poczatkowe
  pinMode(PIN_POMPA, OUTPUT);
  pinMode(PIN_ODPOWIETRZANIE, OUTPUT);
  release_pump();
  serwo.attach(PIN_SERWO);
  serwo.write(SERWO_POZYCJA_SPOCZYNKOWA);
  command_seriali.begin(9600);
}

void auto_loop() { //start programu w petli
  delay(CZAS_OD_WLACZENIA);
  enable_pump();
  delay(CZAS_DZIALANIA_POMPY);
  release_pump();
  delay(CZAS_OPOZNIENIA);
  serwo.write(SERWO_POZYCJA_AKTYWNA);
  delay(CZAS_AKTYWACJA_SERWA);
  serwo.write(SERWO_POZYCJA_SPOCZYNKOWA);
  delay(CZAS_OPOZNIENIA);
}

void read_command(){
  char command = command_serial.read();
  switch(command){
    case ROZKAZ_POMPA_WLACZ:
      enable_pump();
      break;
    case ROZKAZ_POMPA_WYLACZ:
      halt_pump();
      break;
    case ROZKAZ_SERWO_WLACZ:
      serwo.write(SERWO_POZYCJA_AKTYWNA);
      break;
    case ROZKAZ_SERWO_WYLACZ:
      serwo.write(SERWO_POZYCJA_SPOCZYNKOWA);
      break;
    case ROZKAZ_ODPOWIETRZANIE_WLACZ:
      release_pump();
      break;
    default:
      release_pump();
  }
}


void loop(){

}
