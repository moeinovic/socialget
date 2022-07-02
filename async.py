import re
number = (
        ("0" , "0️⃣"),
        ("1" , "1️⃣"),
        ("2" , "2️⃣"),
        ("3" , "3️⃣"),
        ("4" , "4️⃣"),
        ("5" , "5️⃣"),
        ("6" , "6️⃣"),
        ("7" , "7️⃣"),
        ("8" , "8️⃣"),
        ("9" , "9️⃣"),)

def bro(x):
        num = []
        if isinstance(x, int):
            x = str(x)
        for ii,i in enumerate(x):
            for y in number:
                if i in y:
                    num.append(y[1])
        return ''.join(map(str, num))
string = ""
for i in range(39):
    string += f"{string[::-1]} مقابل  🏠 ✈️\n"

with open("bro.txt", "w") as f:
    f.write(string)