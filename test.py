import string




if __name__ == "__main__":
    string ="""dddd
aaaa
bbbb
cccc"""

    newstr = ""
    for line in string.splitlines():
        if line.startswith("a"):
            newstr += "hello\n"
        else:
            newstr += (line+'\n')
        print(newstr)

    newstr = newstr.rstrip()
    print(newstr)
