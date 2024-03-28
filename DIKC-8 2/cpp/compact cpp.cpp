#include <iostream>
#include <fstream>

using namespace std;

string get_raw(string filename) {
    ifstream file;
    file.open(filename);
    string raw = "";
    string line;

    // remove single-line comments, remove line breaks
    while (getline(file, line)) {
        int i = line.find("//");
        if (i != string::npos)
            raw += line.substr(0, i)+" ";
        else raw += line;
    }
    file.close();

    if (raw == "") throw new runtime_error("File is empty");

    // remove tabs
    string _raw = raw;
    raw = "";
    for (int i = 0; i < _raw.length(); i++) {
        if (_raw[i] == '\t') raw += " ";
        else raw += _raw[i];
    }

    // remove multiline comments
    _raw = raw;
    raw = "";
    int index;
    while ((index = _raw.find("/*")) != string::npos) {
        int end = _raw.find("*/");
        if (end == string::npos) throw new runtime_error("Unclosed multiline comment");
        raw += _raw.substr(0, index)+" ";
        _raw = _raw.substr(end+2);
    }
    raw += _raw;

    // separate into words (remove spaces between alnum and non-alnum)
    _raw = raw;
    raw = "";
    bool prev = isalnum(_raw[0]);
    string current = "";
    for (int i = 0; i <= _raw.length(); i++) {
        // force adding the word at the end
        bool now;
        if (i == _raw.length()) now = !prev;
        else now = isalnum(_raw[i]);
        if (now != prev) {
            if (now) {
                if (current == "") raw += " ";
                else raw += current;
            }
            else raw += current;
            current = "";
        }
        if (now) current += _raw[i];
        else if (_raw[i] != ' ') current += _raw[i];
        prev = now;
    }

    return raw;
}

int main() {
    cout << endl << get_raw("scripts/test.dikc2") << endl;
    return 0;
}