from transformers import AutoModelForCausalLM, AutoTokenizer
import kagglehub
import os
import json
import zipfile

def generate_response(qwen, prompt):
    # prepare the model input
    messages = [{"role": "user", "content": prompt}]
    text = qwen[1].apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=True # Switches between thinking and non-thinking modes. Default is True.
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(qwen[0].device)

    # conduct text completion
    generated_ids = qwen[0].generate(**model_inputs, max_new_tokens=32768)
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()

    # parsing thinking content
    try:
        # rindex finding 151668 ()
        index = len(output_ids) - output_ids[::-1].index(151668)
    except ValueError:
        index = 0

    thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
    content = tokenizer.decode(output_ids[index:], skip_special_tokens=True)
    #print(thinking_content)
    return content

def extract_gas_basic_info(qwen, sample):
    template = """Ты - ИИ-помощник, созданный для поиска информации о свойствах газа в тексте и её преобразовании в формат JSON.
Оформи ответ на вопрос в соответствии с примером. В ответе должно быть:
- название основного газа в составе;
- полное название газа;
- химическая формула газа;
- ГОСТ, задающий требования к качеству газа.

ПРИМЕР ВОПРОСА:
НАЗВАНИЕ: Азот жидкий особой чистоты 1 сорт
ГОСТ / НОРМАТИВНЫЙ ДОКУМЕНТ: ГОСТ 9293 - 74
ТРЕБОВАНИЯ К ПРОДУКТУ ПО ГОСТ:
        Наименование показателя                Норма по ГОСТ
        Объёмная доля азота, % не менее                99,999
        Объёмная доля кислорода, % не более                0,0005
        Содержание масла, механических примесей и влаги                выдерживает испытание
        Объёмная доля водорода, % не более                0,0002
        Объёмная доля суммы углеродсодержащих соединений в пересчете на СН4, % не более                0,0003
ОСНОВНЫЕ СВОЙСТВА:
Латинское название:  Nitrogenium
CAS номер: 7727-37-9
UN газа: 1066
UN жидкости: 1977
Код ООН: 1006
Физико-химические свойства:
Электронная конфигурация: 2s22p3
Молекулярая масса: 28.0134
Степень окисления: от +5 до -3
Плотность: 1,251
Удельная теплоёмкость: 1,034
Теплопроводность: 0,026
t кипения: -195,8 °C
t плавления: -210 °C
Внешние признаки: Без цвета вкуса и запаха, химически весьма инертен

ПРИМЕР ОТВЕТА: {"based_on":"на основе Азота","gas_name":"Азот жидкий особой чистоты 1 сорт","formula":"N","state_standard":"ГОСТ 9293 - 74"}
"""
    print("        Извлечение основной информации о газе...")

    raw_response = generate_response(qwen, template + "\nВОПРОС:\n" + sample + "\nОТВЕТ:")

    first_position = raw_response.find("{")
    if first_position == -1:
        print("        ОШИБКА: Qwen3 не дала ответ.")
        print("        Завершено с ошибкой.")
        return None

    last_position = raw_response.find("}", first_position)
    if last_position == -1:
        print("    ОШИБКА: Qwen3 не сгенерировала корректную запись в формате JSON.")
        print("        Завершено с ошибкой.")
        return None

    try:
        result_json = json.loads(raw_response[first_position:last_position + 1])
        print("        Завершено.")
        return result_json
    except:
        print("        ОШИБКА: Не удалось преобразовать основную информацию о газе в JSON-структуру.")
        return None
    
def extract_gas_mark(qwen, sample):
    template = """Извлеки марку из названия газа.
Если марка отсутствует в названии, то вместо марки укажи "Отсутствует".
Оформи ответ в соответствии с примерами.

ПРИМЕР ВОПРОСА 1:
Гелий газообразный высокой чистоты, марка 4.6

ПРИМЕР ОТВЕТА 1:
{"mark":"4.6"}

ПРИМЕР ВОПРОСА 2:
Гелий газообразный высокой чистоты

ПРИМЕР ОТВЕТА 2:
{"mark":"Отсутствует"}

ВОПРОС:
"""
    print("        Извлечение марки газа...")
    raw_response = generate_response(qwen, template + sample + "\n\nОТВЕТ:\n")

    if raw_response.find("{") == -1:
        print("        ОШИБКА: Qwen3 не дала ответ.")

    try:
        result_json = json.loads(raw_response)
        print("        Завершено.")
        return result_json
    except:
        print("        ОШИБКА: Не удалось преобразовать полученную от Qwen3 информацию о марке газа в JSON-структуру.")
        return None
    
def extract_gas_composition(qwen, sample):
    template = """Ты - ИИ-помощник, созданный для поиска информации о составе газа в тексте.
Оформи ответ на вопрос строго в соответствии с примером. Каждый пункт ответа должен включать:
- название компонента газа из вопроса;
- химическую формулу компонента газа из вопроса;
- объёмную долю компонента газа из вопроса.

ПРИМЕР ВОПРОСА:
НАЗВАНИЕ: Азот жидкий особой чистоты 1 сорт
ГОСТ / НОРМАТИВНЫЙ ДОКУМЕНТ: ГОСТ 9293 - 74
ТРЕБОВАНИЯ К ПРОДУКТУ ПО ГОСТ:
        Наименование показателя                Норма по ГОСТ
        Объёмная доля азота, % не менее                99,999
        Объёмная доля кислорода, % не более                0,0005
        Содержание масла, механических примесей и влаги                выдерживает испытание
        Объёмная доля водорода, % не более                0,0002
        Объёмная доля суммы углеродсодержащих соединений в пересчете на СН4, % не более                0,0003
ОСНОВНЫЕ СВОЙСТВА:
Латинское название:  Nitrogenium
CAS номер: 7727-37-9
UN газа: 1066
UN жидкости: 1977
Код ООН: 1006
Физико-химические свойства:
Электронная конфигурация: 2s22p3
Молекулярая масса: 28.0134
Степень окисления: от +5 до -3
Плотность: 1,251
Удельная теплоёмкость: 1,034
Теплопроводность: 0,026
t кипения: -195,8 °C
t плавления: -210 °C
Внешние признаки: Без цвета вкуса и запаха, химически весьма инертен

ПРИМЕР ОТВЕТА:
* Азот - N - не менее 99.999%
* Кислород - O - не более 0.0005%
* Водород - H - не более 0.0002%

ВОПРОС:
"""
    print("        Извлечение состава газа...")
    print("            Извлечение состава газа в виде списка...")

    raw_response = generate_response(qwen, template + sample + "\nОТВЕТ: ")

    composition_list = ""
    for i in raw_response.split('*'):
        composition_list += i
    if len(composition_list) == 0:
        print("            ОШИБКА: Qwen3 не нашла данные о составе продукта.")
        print("        Завершено с ошибкой.")
        return None

    print("            Завершено.")
    print("            Преобразование списка в запись в формате JSON...")

    template = """Ты - ИИ-помощник, преобразующий списки в данные в формате JSON.
Оформи ответ на вопрос в соответствии с примером.

ПРИМЕР ВОПРОСА:
* Азот - N - не менее 99,999%
* Кислород - O - не более 0,0005%
* Водород - H - не более 0,0002%

ПРИМЕР ОТВЕТА: {"components":[{"name":"Азот","formula":"N","value":"99.999","operation":"не менее"},{"name":"Кислород","formula":"O","value":"0.0005","operation":"не более"},{"name":"Водород","formula":"H","value":"0.0002","operation":"не более"}]}

ВОПРОС:
"""
    response = generate_response(qwen, template + composition_list + "\n\nОТВЕТ: ")

    #Особенность конкретно Qwen3. Периодически она выдаёт в ответе ```json<ОТВЕТ>```.
    if response[0] == '`':
        response = response[7:len(response) - 3]

    try:
        result_json = json.loads(response)
        print("        Завершено.")
        return result_json
    except:
        print("        ОШИБКА: Не удалось преобразовать полученную от Qwen3 информацию о составе газа в JSON-структуру.")
        return None
    
def extract_info(qwen, dataset):
    extracted_info = [[], [], []]
    extraction_error_count = [0, 0, 0]

    #файл 24 - хороший пример
    print("Извлечение информации из датасета...")
    for i in range(0,len(dataset)):
        print("    Обработка файла " + str(i) + "/" + str(len(dataset)) + "...")

        extracted_basic_info = extract_gas_basic_info(qwen, dataset[i])
        extracted_info[0].append(extracted_basic_info)
        if extracted_basic_info == None:
            extraction_error_count[0] += 1
        else:
            if "gas_name" in extracted_basic_info:
                extracted_mark = extract_gas_mark(qwen, extracted_basic_info["gas_name"])
                extracted_info[1].append(extracted_mark)
                if extracted_mark == None:
                    extraction_error_count[1] += 1
            else:
                extracted_info[1].append(None)

        extracted_composition = extract_gas_composition(qwen, dataset[i])
        extracted_info[2].append(extracted_composition)
        if extracted_composition == None:
            extraction_error_count[2] += 1

    print(("Завершено ("
           + str(extraction_error_count[0])
           + " ошибок извлечения основной информации, "
           + str(extraction_error_count[1])
           + " ошибок извлечения информации о марке газа, "
           + str(extraction_error_count[2])
           + " ошибок извлечения состава)."))

    return extracted_info

def load_dataset(dataset_path):
    if not os.path.isdir(dataset_path):
        if not os.path.isfile(dataset_path):
            raise Exception("Error: file not found.")

        name, extension = os.path.splitext(dataset_path)
        print(extension)
        if extension == ".zip":
            with zipfile.ZipFile(dataset_path, 'r') as zip_ref:
                zip_ref.extractall(name)
            dataset_path = name
        else:
            raise Exception("Error: unsupported file type.")

    dataset_file_names = os.listdir(dataset_path)

    dataset = []
    loaded_file_count = 0
    ignored_file_count = 0

    print("Загрузка датасета...")
    for i in dataset_file_names:
        f = open(dataset_path + "/" + i, 'r', encoding="utf-8")

        #Файлы, не содержащие информацию о ГОСТ или другом нормативном документе, игнорируются.
        buffer = f.readlines()
        ignore = True
        for j in buffer:
            if j.find("ГОСТ") != -1:
                ignore = False
                break
        if ignore:
            print("    ПРЕДУПРЕЖДЕНИЕ: Файл \"" + i + "\" не содержит информацию о ГОСТ. Файл пропущен.")
            ignored_file_count += 1
        else:
            loaded_file_count += 1
            buffer2 = ""
            for j in buffer:
                buffer2 += j
            dataset.append(buffer2)

        f.close()

    print("Завершено (" + str(len(dataset_file_names)) + " всего, " + str(loaded_file_count) + " загружено, " + str(ignored_file_count) + " пропущено).")
    return dataset

#############################

import argparse
import sys

params = argparse.ArgumentParser(description=
"""Extracts information about gases from the dataset using Alibaba Qwen3 0.6b and stores it in a text file.""",
formatter_class=argparse.RawDescriptionHelpFormatter, epilog=
"""EXAMPLE

python qwen3_json_generator.py -d dataset.zip -k credentials.json -o output.json

Decompress "dataset.zip" to "dataset", load files from "dataset", load Kaggle credentials from "credentials.json", extract the data using Alibaba Qwen3 0.6b and save the extracted data into the "output.json".""")

params.add_argument("-d", "--dataset-path", type=str, help="Path to the dataset. Must be a directory or a zip archive.")
params.add_argument("-k", "--kaggle-credentials-path", type=argparse.FileType('r'), help="Path to JSON file that contains Kaggle credentials. Credentials have the following structure: {\"username\":\"<STRING>\",\"key\":\"<STRING>\"}")
params.add_argument("-o", "--output", type=argparse.FileType('w'), help="An output text file name. If the parameter is missing, the name will default to \"qwen3_extracted_info.json\".")

params = params.parse_args()

if not params.dataset_path:
    sys.exit("Path to the dataset is not specified. Exiting.")
if not params.kaggle_credentials_path:
    sys.exit("File with Kaggle credentials is not specified. Exiting.")

kaggle_credentials = None
try:
    kaggle_credentials = json.loads(params.kaggle_credentials_path.read())
except:
    sys.exit("Incorrect Kaggle credentials format. Exiting.")
if not "username" in kaggle_credentials or not "key" in kaggle_credentials:
    sys.exit("Incorrect Kaggle credentials format. Exiting.")

dataset = None
try:
    dataset = load_dataset(params.dataset_path)
except:
    sys.exit("Unable to load the dataset. Exiting.")

os.environ["KAGGLE_USERNAME"] = kaggle_credentials["username"]
os.environ["KAGGLE_KEY"] = kaggle_credentials["key"]
model_name = kagglehub.model_download("qwen-lm/qwen-3/transformers/0.6b")
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype="auto", device_map="auto")

output_file = params.output if params.output else open("qwen3_extracted_info.json", "w")    
extracted_info = extract_info((model, tokenizer), dataset)
output_file.write(json.dumps(extracted_info,ensure_ascii=False,indent=4))
output_file.close()