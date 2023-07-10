#define TX_PIN LED_BUILTIN
#define BIT_TIME_1 800 // in us
#define BIT_TIME_0 200
#define BIT_TIME 1000
#define SRC 0x1337

char packet[5] = {0};

void send_bit(bool to_send){
  if (to_send){
    digitalWrite(TX_PIN, 1);
    delayMicroseconds(BIT_TIME_1);
    digitalWrite(TX_PIN, 0);
    delayMicroseconds(BIT_TIME_0);
  }else{
    digitalWrite(TX_PIN, 1);
    delayMicroseconds(BIT_TIME_0);
    digitalWrite(TX_PIN, 0);
    delayMicroseconds(BIT_TIME_1);
  }
}

void reset_tx(){
  digitalWrite(TX_PIN, LOW);
}

void build_packet(int to_send){
  packet[1] = to_send & 0xFF;
  packet[2] = 0;
  packet[3] = SRC & 0xFF;
  packet[4] = (SRC >> 8) & 0xFF;
}

void send_packet(){
  for(int i = 0; i < sizeof(packet); i++){
    char c = packet[i];
    for(int j = 0; j < 8; j++){
      send_bit(c & 1);
      c = c >> 1;
    }
  }
  reset_tx();
}

void print_packet(){
  for(int i = 1; i < sizeof(packet); i++){
    unsigned char c = packet[i];
    Serial.print(c, DEC);
    Serial.print(" ");
  }
  Serial.println("");
}

void setup() {
  pinMode(TX_PIN, OUTPUT);
  pinMode(A0, INPUT);

  Serial.begin(115200);

  packet[0] = 0b01010101;
}

void loop() {
  if(Serial.available() > 0){
    int to_send = Serial.read();
    build_packet(to_send);
    send_packet();
    print_packet();
  }
  delay(1);
}
