//gcc -m32 -o emojifier file.c -fno-stack-protector -no-pie
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

#define MAX_LEN 360
#define MAX_INPUT 109
#define NUM_EMOJI 10



typedef struct
{
    char code[20];
    char symbol[40]; 
} Emoji;

void init(){
    setvbuf(stdin, 0, 2, 0);
    setvbuf(stdout, 0, 2, 0);
}


void initEmojis(Emoji *em){
    int i;
    
    strcpy(em[0].code , ":sob:"); //14
    strcpy(em[0].symbol, ";´༎ຶД༎ຶ`)"); // rapporto 3.33
    
    strcpy(em[1].code , ":cute:"); // 14
    strcpy(em[1].symbol, "(｡◕‿‿◕｡)"); // rapporto 3

    strcpy(em[2].code , ":creep:"); // 8
    strcpy(em[2].symbol, "ԅ(≖‿≖ԅ)"); // rapporto 2

    strcpy(em[3].code , ":blush:"); //14
    strcpy(em[3].symbol, "(˵ ͡° ͜ʖ ͡°˵)"); // rapporto 2.75

    strcpy(em[4].code , ":bat:"); // 8
    strcpy(em[4].symbol, "/|\\ ^._.^ /|\\"); //rapporto 2.33

    strcpy(em[5].code , ":arrowhead:"); // 8
    strcpy(em[5].symbol, "⤜(ⱺ ʖ̯ⱺ)⤏"); // rapporto 1.60

    strcpy(em[6].code , ":flower:"); //6
    strcpy(em[6].symbol, "(✿◠‿◠)"); // rapporto 1.66

    strcpy(em[7].code , ":gimme:"); //15
    strcpy(em[7].symbol, "༼ つ ◕_◕ ༽つ"); //rapporto 2.87

    strcpy(em[8].code , ":hadouken:"); //24
    strcpy(em[8].symbol, "༼つಠ益ಠ༽つ ─=≡ΣO))"); // rapporto 3.18    

    strcpy(em[9].code, ":damnyou:"); //14
    strcpy(em[9].symbol, "(ᕗ ͠° ਊ ͠° )ᕗ"); // rapporto 2.40
}


int findSubstringPosition(const char *haystack, const char *needle){
    int i;
    for(i=0; i<MAX_LEN-strlen(needle); i++){
        if( strncmp(&haystack[i], needle, strlen(needle)) == 0) {
            return i;
        } 
    } 
    return -1;
}

void insertString(char* destination, int pos, char* seed, int *usedS){
    memmove(&destination[pos+strlen(seed)], &destination[pos] , *usedS-pos); //MAX_LEN-pos-strlen(seed)
    memmove(&destination[pos], seed, strlen(seed));
}

void shiftString(char *buf, int pos, int shift, int *usedS){
    memmove(&buf[pos+shift], &buf[pos], *usedS-pos);
    *usedS += shift;
}
void placeSymbol(char *buf, char *symbol, int pos){
    memcpy(&buf[pos], symbol, strlen(symbol));
}

void editString( char *buf, Emoji *em){
    int usedSpace = MAX_INPUT;
    int i, pos;
    for(i=0;i<NUM_EMOJI; i++){
        while( (pos = findSubstringPosition(buf, em[i].code) ) != -1 ){
            shiftString(buf, pos + strlen(em[i].code), strlen(em[i].symbol) - strlen(em[i].code) , &usedSpace);
            placeSymbol(buf, em[i].symbol, pos);
        }
    }
    insertString(buf, 0, "Thank you for using me. I really appreciate it! Bip bop.\n>>> ", &usedSpace);

}


int countString(const char *haystack, const char *needle){
    int count = 0;
    const char *tmp = haystack;
    while(tmp = strstr(tmp, needle))
    {
        count++;
        tmp++;
    }
    return count; 
}

int countAllEmoji(const char *buf, Emoji *em){
    int i;
    int counter = 0;
    for (i =0 ; i<NUM_EMOJI; i++){
        counter += countString(buf, em[i].code);
    }
    return counter;
}


void welcome(){
    puts("This is emojifier 1.0!\n");
    puts("Gimme some text with emotions:\n");
}

void AuRevoir(){
    puts("Bye bye! Bip Bop");
}

void printEmojized(char *buf){
    puts("########");
    printf("%s\n", buf);
    puts("########");
}

void emojifier(){
    char buffer[MAX_LEN];
    int emojiCount;
    Emoji emojis[NUM_EMOJI];
    initEmojis(emojis);
    memset(buffer,0,MAX_LEN);
    fgets(buffer, MAX_INPUT+1, stdin);
    emojiCount = countAllEmoji(buffer, emojis);
    if (emojiCount > 10){
        puts("Too many emotions for a program! Bip Bop.");
        exit(1);
    }
    editString(buffer, emojis);
    printEmojized(buffer);
}


int main(){
    init();
    welcome();
    emojifier();
    AuRevoir();
    return 0;

}