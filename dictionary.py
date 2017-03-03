import urllib.request
import xml.etree.ElementTree as ET
from key import *
import json
"""
<entry id="test[4]">
<ew>test</ew>
<subj>ZI</subj>
<hw hindex="4">test</hw>
<fl>noun</fl>
<et>
Latin
<it>testa</it>
shell
</et>
<def>
<date>circa 1842</date>
<dt>
:an external hard or firm covering (as a shell) of many invertebrates (as a foraminifer or a mollusk)
</dt>
</def>
</entry>
"""
def process_dt(dt):
    return_str = ""
    if dt.text:
        return_str+= dt.text.strip()
    for each_child in dt:
        return_str += (" " + process_dt(each_child)+ " ")
    if dt.tail:
        return_str+= dt.tail.strip()
    return_str = return_str.strip()
    if dt.tag == 'sxn':
        return_str = ''
    elif dt.tag == 'sx':
        return_str = "#Synonymous: "+ return_str
    elif dt.tag == 'un':
        return_str = "\n  #Usage: " + return_str
    elif dt.tag == 'pr':
        return_str = ""
    elif dt.tag == 'vi':
        return_str = "\n  #Ex: " + return_str
    elif dt.tag == 'aq':
        return_str = ""
    return return_str

    """

    {bc}
    BOLDFACE COLON (has special significance)
    -- requires no-break space after

    <sx>...</sx>    (text = small caps except after <sxn>)
    | SYNONYMOUS CROSS REF TARGET --small caps
    |  (small caps ends with first </sx> or <sxn> tag)
    | -- may contain one or more <sxn> subfields
    | -- single word space follows unless COMMA RULE applies
    |
    |<sxn>...</sxn> (text = roman)
    |  SYNONYMOUS CROSS REF SENSE NUMBER 
    |  (defaults out of small caps to normal roman)
    |  if two or more <sxn> fields occur together
    |   they must be separated by a generated comma (+ space)

    <un>...</un>    (text = roman)
    | USAGE NOTE, following or replacing defining text;
    | first occurrence introduced by a light em dash 
    |   (implied by the opening tag)    
    | <un> field may contain one or more <vi> fields
    | - followed by single space unless COMMA RULE applies

    <ca>...</ca>    (text = roman)
    | CALLED ALSO element; 
    | contains words "called also " and one or more <cat> subfields
    |   and possibly <pr> fields
    |  -- first occurrence, if there is no prior <un> field, 
    |    generates opening light em dash
    | - followed by single space unless COMMA RULE applies
    |
    |<cat>...</cat> (text = italic)
    |  CALLED ALSO TARGET
    |  Two or more <cat> fields need to be 
    |    separated by a generated comma
    |   -- if a <pr> field comes between two <cat> fields
    |   the comma separates <pr> field from following <cat> field

    <vi>...</vi>    (text = roman)
    |VERBAL ILLUSTRATION
    |-- tags must generate opening and closing angle brackets
    | may contain <aq> subfield
    | -- single word space follows <vi> field
    |
    |<aq>...</aq>   (text = roman)
    |  AUTHOR QUOTED 
    |  --opening tag must generate lightface em dash, 
    |  (space before, no space after)

    <dx>...</dx>    (text = roman)
    | DIRECTIONAL CROSS-REFERENCE
    | -- contains words "see" or "compare" and <dxt> subfield(s)
    | -- single word space follows <dx> field unless SEMICOLON RULE applies
    | -- first occurrence (if there is no prior <un> or <ca>) 
    |       generates initial light em dash;
    | See COMMA RULE above
    |
    |<dxt>...</dxt> (text = small caps)
    | target word/element; 
    | (small caps ends with first </dxt> or <dxn> tag)  
    | -- <dxt> field may contain <dxn> subfield
    |
    |<dxn>...</dxn> (text = roman)
    |  DIRECTIONAL CROSS REF NUMBER
    |  (defaults out of small caps to normal roman)
    |  -- used for cross-ref sense number (numeral) or 
    |  a word like "table" or "illustration" that is part 
    |  of the target

    |<sd>...</sd>   (text = italic)
    | SENSE DIVIDER ("also", "esp", "specif", "broadly") 
    | -- opening tag must generate a semicolon (+ space) to
    |   separate this from previous text
    | -- single word space follows, unless COMMA RULE applies

    <math></math>   (no text)
        empty field to mark place within the <dt> field for 
        inserting math formula id'd in <formula> field

"""



def process_def(definiation):
    return_list = []
    for each_tag in definiation:
        if each_tag.tag == "dt":
            return_list.append(process_dt(each_tag))
    return return_list

def process_entry(entry):
    entry_dict = {"definiation":[]}
    entry_dict["word"] = entry[0].text
    fl_tag = entry.find('fl')   
    if fl_tag is not None:
        entry_dict["part"] = fl_tag.text
    for eachDef in entry.findall('def'):
        entry_dict["definiation"].append(process_def(eachDef))
    return entry_dict

def process_root(root):
    for child in root:
        process_entry(child)

def load_json(filename):
    try:
        file = open(filename,'r')
        return_json = json.load(file)
        file.close()
        return return_json
    except Exception as e:
        print(e)
        return None

def print_defination(definiation):
    for each_tag in definiation:
        print(each_tag)

def print_explanation(explanation):
    print("@Word:{}".format(explanation['word']))
    if 'part' in explanation:
        print("@This is {}".format(explanation['part']))
    i = 0
    for each in explanation['definiation']:
        print("#{}. ".format(str(i)))
        print_defination(each)
        i+=1
    


def print_word(word_dict, explanations = True, extensions =False):
    explanation_list = word_dict['explanations']
    if explanations:
        print("Explanations:")
        i = 0
        for each in explanation_list:
            print("----------------{}------------------".format(str(i)))
            print_explanation(each)
            print("----------------------------------" + '-' * ((i//10)+1) )
            i+=1
    extentions_list = word_dict['extensions']
    if extensions or len(explanation_list) == 0:
        print("Extentions:")
        i = 0
        for each in extentions_list:
            print("----------------{}------------------".format(str(i)))
            print_explanation(each)
            print("----------------------------------" + '-' * ((i//10)+1) )
            i+=1

def print_suggestions(suggestions):
    print("Not found, maybe you mean?")
    i = 0
    for each in suggestions:
        print("{}. {}".format(str(i), each))
        i+=1

def search_word(user_input, database):
    input_list = user_input.strip().split('@')
    word = input_list[0]
    should_show_extension = False
    if len(input_list) > 1:
        should_show_extension = input_list[1] == 'e'
    print("You are searching for {}".format(word))
    if word in stored_json:
        stored_json[word]['hit'] += 1
        print("Find local cache:")
        print("You have search for {} times".format(word), stored_json[word]['hit'])
        print_word(stored_json[word], extensions = should_show_extension)
    else:
        url = "http://www.dictionaryapi.com/api/v1/references/collegiate/xml/{}?key={}".format(word, api_key)
        try:
            response = urllib.request.urlopen(url)
            response_str = response.read()
            root = ET.fromstring(response_str)
            suggestions = []
            explanations = []
            extensions = []
            for child in root:
                if child.tag == 'suggestion':
                    suggestions.append(child.text)
                elif child.tag == 'entry':
                    if (child[0].text.lower() == word.lower()):
                        explanations.append(process_entry(child))
                    else:
                        extensions.append(process_entry(child))
            if len(explanations) == 0 and len(extensions) == 0:
                if len(suggestions) == 0:
                    print("Not found")
                else:
                    print_suggestions(suggestions)
            else:
                word_dict = {'explanations':explanations, 'extensions':extensions, 'hit':1}
                database[word] = word_dict
                print_word(word_dict, extensions = should_show_extension)
        except Exception as e:
            print("Error", e)

def save(database, filename):
    f = open(filename, 'w')
    json.dump(database,f ,sort_keys=True,indent=4, separators=(',', ': '))
    f.close()

if __name__ == '__main__':
    stored_json = load_json(storage_file)
    if stored_json is None:
        stored_json = {}

    while 1:
        entered = input("Please enter your word\n")
        if not entered:
                break
        else:
            search_word(entered, stored_json)
            save(stored_json, storage_file)
            print()







