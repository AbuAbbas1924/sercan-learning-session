import jwt

MY_KEY = "nahdah"
MY_KEY2 = "salam"


msg = {"msg": "hallo"}
# print("msg", msg)
# encoded = jwt.encode(msg, MY_KEY, algorithm="HS256")
# print("encoded", encoded)
# decoded = jwt.decode(encoded, MY_KEY2, algorithms="HS256")
# print("decoded", decoded)

def encoding(arg1, arg2):
    try: 
        encoded = jwt.encode(arg1, arg2, algorithm="HS256")
        print(f"encoded output: {encoded}")
        return encoded
    except:
        print("Encoding doesnt work")

def decoding(arg1, arg2):
    try:
        decoded = jwt.decode(arg1, arg2, algorithms="HS256")
        print(f"decoded output: {decoded}")
    except:
        print("decoding failed the key is wrong")

if __name__ == "__main__":
    enc = encoding(msg, MY_KEY2)
    decoding(enc, MY_KEY2)
 
