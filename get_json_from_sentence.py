import subprocess
import json

def run_apertium_command(input_text):
    # Команданы даярдоо
    command = f'echo "{input_text}" | apertium -d . kir-seg'
    
    # Команданы аткаруу
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    # Натыйжаны кайтаруу
    return result.stdout

def extract_base_words(segmented_text):
    # Натыйжаны саптарга бөлүү
    words = segmented_text.strip().split()
    
    known_words = []
    unknown_words = []

    for word in words:
        if '*' in word:
            # Белгисиз сөздөрдү белгилейбиз
            base_form = word.replace('*', '')
            unknown_words.append(base_form)
        else:
            # Керектүү бөлүгүн бөлүү (сөздөгү баштапкы формасын алуу)
            base_form = word.split('>')[0]
            known_words.append(base_form)
    
    return known_words, unknown_words

# Киргизүү текстин аныктоо
input_text = "Мен китептерди тапшырганы кезекте туруп, трансценденталдык абалга түшүп калдым."

# Команданы иштетүү жана натыйжаны алуу
segmented_text = run_apertium_command(input_text)

# Негизги сөздөрдү алуу
known_words, unknown_words = extract_base_words(segmented_text)

# Натыйжаны JSON форматка келтирүү
result = {
    "known": known_words,
    "unknown": unknown_words
}

# Натыйжаны JSON форматта чыгаруу
print(json.dumps(result, ensure_ascii=False, indent=4))
