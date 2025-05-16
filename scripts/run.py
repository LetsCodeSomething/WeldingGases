import os
import sys
import json
import argparse
import subprocess

params = argparse.ArgumentParser(description=
"""Loads the parameters for other scripts in the same directory that contains \"run.py\" from the specified JSON file and executes all other scripts in the following order: \"niikm_parser.py\" ---> \"gemma_json_generator.py\" ---> \"json_comparator.py\" ---> \"json_converter.py\".
The configuration file must have this structure:

{
    "niikm_parser":
    {
        "request_delay": <INTEGER VALUE IN [0; 20]>,
        "output_dir": <STRING VALUE>,
        "zip": <"true"/"false">
    },
    "gemma_json_generator":
    {
        "dataset_path": <STRING VALUE>,
        "kaggle_credentials_path": <STRING VALUE>,
        "output": <STRING VALUE>
    },
    "json_comparator":
    {
        "left_json": <STRING VALUE>,
        "right_json": <STRING VALUE>,
        "output": <STRING VALUE>
    },
    "json_converter":
    {
        "input": <STRING VALUE>,
        "user_email": <STRING VALUE>,
        "infores_name": <STRING VALUE>
    }
}          

Please note that this script checks the existence of the parameters for other scripts and not their values.""",
formatter_class=argparse.RawDescriptionHelpFormatter, epilog=
"""EXAMPLE

python run.py --config-path config.json

Load the parameters for other scripts from \"config.json\" and launch other scripts.""")

params.add_argument("--config-path", type=argparse.FileType('r',encoding="utf-8"), help="Path to the configuration file.")

params = params.parse_args()

if not params.config_path:
    sys.exit("The configuration file is missing. Exiting.")

#Check the JSON structure.
configuration = None
try:
    configuration = json.loads(params.config_path.read())
except:
    sys.exit("The specified configuration file contains invalid JSON. Exiting.")

if (not "niikm_parser" in configuration or
    not "gemma_json_generator" in configuration or
    not "json_comparator" in configuration or
    not "json_converter" in configuration): 
    sys.exit("The specified configuration file contains invalid JSON. Exiting.")

if (not "request_delay" in configuration["niikm_parser"] or
    not "output_dir" in configuration["niikm_parser"] or
    not "zip" in configuration["niikm_parser"]):
    sys.exit("The specified configuration file contains invalid JSON. Exiting.")

if (not "dataset_path" in configuration["gemma_json_generator"] or
    not "kaggle_credentials_path" in configuration["gemma_json_generator"] or
    not "output" in configuration["gemma_json_generator"]):
    sys.exit("The specified configuration file contains invalid JSON. Exiting.")

if (not "left_json" in configuration["json_comparator"] or
    not "right_json" in configuration["json_comparator"] or
    not "output" in configuration["json_comparator"]):
    sys.exit("The specified configuration file contains invalid JSON. Exiting.")

if (not "input" in configuration["json_converter"] or
    not "user_email" in configuration["json_converter"] or
    not "ontology_path" in configuration["json_converter"] or
    not "chem_db_path" in configuration["json_converter"] or
    not "output_infores_path" in configuration["json_converter"] or
    not "ouptut" in configuration["json_converter"]):
    sys.exit("The specified configuration file contains invalid JSON. Exiting.")

#Check if other scripts exist.
directory_path = os.path.dirname(os.path.abspath(__file__))

niikm_parser_path = os.path.join(directory_path, "niikm_parser.py")
gemma_json_generator_path = os.path.join(directory_path, "gemma_json_generator.py")
json_comparator_path = os.path.join(directory_path, "json_comparator.py")
json_converter_path = os.path.join(directory_path, "json_converter.py")

if not os.path.isfile(niikm_parser_path):
    sys.exit("\"niikm_parser.py\" is missing. Exiting.")
if not os.path.isfile(gemma_json_generator_path):
    sys.exit("\"gemma_json_generator.py\" is missing. Exiting.")
if not os.path.isfile(json_comparator_path):
    sys.exit("\"json_comparator.py\" is missing. Exiting.")
if not os.path.isfile(json_converter_path):
    sys.exit("\"json_converter.py\" is missing. Exiting.")

#Run the scripts.
print("Running \"niikm_parser.py\"...")
zip_parameter = " --zip" if configuration["niikm_parser"]["zip"] == "true" else ""
process = subprocess.Popen("python \"" + str(niikm_parser_path) + 
                           "\" --request-delay \"" + str(configuration["niikm_parser"]["request_delay"]) +
                           "\" --output-dir \"" + configuration["niikm_parser"]["output_dir"] +
                           zip_parameter, encoding="utf-8", shell=True)
if process.wait() != 0:
    print("\"niikm_parser.py\" finished with an error. Exiting.")
print("Done.")

print("Running \"gemma_json_generator.py\"...")
process = subprocess.Popen("python \"" + str(gemma_json_generator_path) + 
                           "\" --dataset-path \"" + configuration["gemma_json_generator"]["dataset_path"] +
                           "\" --kaggle-credentials-path \"" + configuration["gemma_json_generator"]["kaggle_credentials_path"] +
                           "\" --output \"" + configuration["gemma_json_generator"]["output"] + "\"", encoding="utf-8", shell=True)
if process.wait() != 0:
    print("\"gemma_json_generator.py\" finished with an error. Exiting.")
print("Done.")

print("Running \"json_comparator.py\"...")
process = subprocess.Popen("python \"" + str(json_comparator_path) + 
                           "\" --left-json \"" + configuration["json_comparator"]["left_json"] +
                           "\" --right-json \"" + configuration["json_comparator"]["right_json"] +
                           "\" --output \"" + configuration["json_comparator"]["output"] + "\"", encoding="utf-8", shell=True)
if process.wait() != 0:
    print("\"json_comparator.py\" finished with an error. Exiting.")
print("Done.")

print("Running \"json_converter.py\"...")
process = subprocess.Popen("python \"" + str(json_converter_path) + 
                           "\" --input \"" + configuration["json_converter"]["input"] + 
                           "\" --user-email " + configuration["json_converter"]["user_email"] +
                           " --ontology-path \"" + configuration["json_converter"]["ontology_path"] +
                           "\" --chem-db-path \"" + configuration["json_converter"]["chem_db_path"] +
                           "\" --infores-name \"" + configuration["json_converter"]["infores_name"] + 
                           "\" --output \"" + configuration["json_converter"]["output"] + "\"", 
                           encoding="utf-8", shell=True)
if process.wait() != 0:
    sys.exit("\"json_converter.py\" finished with an error. Exiting.")
print("Done.")