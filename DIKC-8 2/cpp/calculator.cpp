#include <iostream>

using namespace std;

struct Node;
typedef struct {
    string type;
    Node* left;
    Node* right;
} Node;

int to_number(string s) {
    int number = 0;
    for (int i = 0; i < s.length(); i++) {
        number = number*10 + s[i]-'0';
    }
    return number;
}

int eval(string s) {
    string current = "";
    bool prev = isalnum(s[0]);
    int prev_number;
    string prev_operator;
    bool first = true;

    for (int i = 0; i < s.length(); i++) {
        char now = isalnum(s[i]);
        if (prev == now) current += s[i];
        else {
            if (now) {
                prev_number = to_number(current);
                if (!first) {
                    
                }
                first = false;
            }
            else prev_operator = current;
        }
        prev = now;
    }
}

int main() {
    cout << eval("1+2*3") << endl;
}