import click
import json
import logging
import os
import ruamel.yaml

toBeSkipped = ['load_avg.json','agent_version.json']
yaml =ruamel.yaml.YAML()

def is_sensitive(key):
    if 'access_' in key or 'Password' in key or 'pass' in key or key.endswith('_key') or key.endswith('secret'):
        return True
    else:
        return False


def get_all_values(nested_dictionary):
    for key, value in nested_dictionary.items():
        if type(value) is dict or str(type(value)) == '<class \'ruamel.yaml.comments.CommentedMap\'>':
            get_all_values(value)
        else:
            if is_sensitive(key):
                nested_dictionary[key] = 'redacted'

# For redacting information from Diagnostic Tarball.
@click.command()
@click.argument('dir_name')
def remove_sensitive_info(dir_name):
    not_processed = []
    for subdir, dirs, files in os.walk(dir_name):
        for fileName in files:
            try:
                filepath = subdir + os.sep + fileName
                if fileName in toBeSkipped or os.stat(filepath).st_size==0:
                    continue

                if filepath.endswith("yaml"):
                    print(f"redacting {fileName}...")
                    with open(filepath, 'r') as openFile:
                        yamlDict = yaml.load(openFile)
                        get_all_values(yamlDict)
                        with open(filepath, 'w') as outFile:
                            yaml.dump(yamlDict, outFile)

                elif filepath.endswith("json"):
                    print(f"redacting {fileName}...")
                    with open(filepath) as openFile:
                        jsonDict = json.load(openFile)
                        get_all_values(jsonDict)
                        with open(filepath, 'w') as outFile:
                            json.dump(jsonDict, outFile, indent=4, sort_keys=True)
                
                elif filepath.endswith("conf"):
                    print(f"redacting {fileName}...")
                    conf_file_lines = []
                    with open(filepath) as openFile:
                        for line in openFile:
                            if line.startswith('#') or line == '\n':
                                conf_file_lines.append(line)
                                continue
                            tokens = line.split(maxsplit=1)
                            if is_sensitive(tokens[0]):
                                conf_file_lines.append(f"{tokens[0]}  redacted")
                            else:
                                conf_file_lines.append(line)
                    with open(filepath, 'w') as outFile:
                        for line in conf_file_lines:
                            outFile.write(line)

            except (Exception) as e:
                not_processed.append([fileName,e])
                continue

    for not_processed_file in not_processed:
        print("Can't completely remove sensitive information in directory %s, got %s" % (not_processed_file[0], not_processed_file[1]))