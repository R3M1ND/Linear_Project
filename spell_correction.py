dictionary = set()

def read_dictionary_file():
    global dictionary
    if dictionary:
        return

    with open("dictionary.txt", "r") as file:
        contents = file.read()

    dictionary = set(word.lower() for word in contents.splitlines())

def is_spelled_correctly(word):
    read_dictionary_file()
    word = word.lower()

    return word in dictionary

if __name__ == "__main__":
    value = input("enter words : ")
    value = value.strip(".,\"!:;?").split()

    for word in value:
        if not is_spelled_correctly(word):
            print("NOT SPELLED CORRECTLY :",word)


