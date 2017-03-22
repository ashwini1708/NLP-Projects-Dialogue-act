import os
import glob
import sys
import csv
import json

def read_file(dialog_filename):


    with open(dialog_filename, "r") as dialog_csv_file:
        reader = csv.DictReader(dialog_csv_file)
        tag_list=[]
        for each_item in reader:
            tag_list.append(each_item['act_tag'])

    return tag_list

def read_output_file(output_file):
    outer_list=[]
    innerList = []
    for line in output_file:

        if 'Filename=' not in line:
            innerList.append(json.loads(line))
        elif "Filename=" in line:
            outer_list.append(innerList)
            innerList=[]

    return outer_list

def main():
    actual_tag=[]
    dialog_filenames = sorted(glob.glob(os.path.join(sys.argv[1], "*.csv")))
    for dialog_filename in dialog_filenames:
        actual_tag.append(read_file(dialog_filename))

    record=[]
    file=open(sys.argv[2], 'r')
    innerList=[]
    for line in file:
        strippedString = line.strip()
        if 'Filename=' not in line:
            innerList.append(line.replace("\n",""))
        if strippedString=="":
            record.append(innerList)
            innerList=[]

    total_counter=0
    correct_counter=0
    for each_list in range(len(actual_tag)):
        actual_tag_list=actual_tag[each_list]
        pred_tag_list=record[each_list]
        for each_index in range(len(actual_tag_list)):

            total_counter=total_counter+1
            if(actual_tag_list[each_index]==pred_tag_list[each_index]):
                correct_counter=correct_counter+1

    print("Correct counter:", correct_counter)
    print("Total counter is:", total_counter)
    accuracy=(correct_counter/total_counter) * 100
    print("Accuracy : ",accuracy)



if __name__ == "__main__":
    main()