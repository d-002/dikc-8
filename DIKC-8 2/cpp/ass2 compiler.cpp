#include <iostream>
#include <fstream>
#include <stdexcept>

using namespace std;

void compile(string filename) {
    ifstream file;
    if (!file.good()) throw invalid_argument("File not found");

    file.open(filename);
    string raw = "";
    string line;

    // remove comments, remove line breaks
    while (getline(file, line)) {
        int i = line.find(';');
        if (i != string::npos)
            raw += line.substr(0, i) + ' ';
        else raw += line + ' ';
    }
    file.close();

    // remove extra spaces
    string code = "";
    char prev = ' ';
    for(int i = 0; i < raw.length(); i++) {
        if ((prev != ' ' || raw[i] != ' ') && raw[i] != '\t' && raw[i] != '\r') code += raw[i];
        prev = raw[i];
    }

    cout << code << endl;
}

int main() {
    compile("scripts/test.ass2");
    return 0;
}