import urllib.request
import xml.etree.ElementTree as ET
from key import *
import json
import regex
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
def process_dt2(dt):
    if (dt.tag == 'sxn'):
        return ""
    return_str = ""
    if dt.text:
        return_str+= dt.text
    for each_child in dt:
        return_str += process_dt2(each_child)
    if dt.tail:
        return_str+= dt.tail
    return return_str


def process_dt(dt):
    return_str = ""
    tag_mapping = {"<sx>":"", "<sxn>":"" , "{bc}"}
    for each_tag in dt:
        if each_tag.tag == "sx":

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
    fl = entry.find('fl')
    if fl:
        entry_dict["part"] = fl.text

    for eachDef in entry.findall('def'):
        entry_dict["definiation"].append(process_def(eachDef))
    return entry_dict

if __name__ == '__main__':
    while 1:
        entered = input("Please enter your word")
        if not entered:
                break
        else:
            word = entered.strip()
            print("You are searching for {}".format(word))
            url = "http://www.dictionaryapi.com/api/v1/references/collegiate/xml/{}?key={}".format(word, api_key)
            try:
                response = urllib.request.urlopen()
                response_str = response.read()
                tree = ET.fromstring(response_str)
                root = tree.getroot()

                suggestions = []
                explanation = []
                found = False
                for child in root:
                    if child.tag == 'suggestion':
                        suggestions.append(child.text)
                    elif child.tag == 'entry':
                        if (child[0].text.lower() == word.lower()):
                            explanation.append(processEntry(child))
            except Exception as e:
                print("Error", e)


