from hw3_corpus_tool import get_data
import pycrfsuite
import sys
import os
import glob
import json
import string


jenc = json.JSONEncoder();
trainer = pycrfsuite.Trainer(verbose=False)


def word2features(utterance, i):
    if i == 0:
        prev_speaker = utterance[0].speaker
        firstUtterance = True
    else:
        prev_speaker = utterance[i - 1].speaker
        firstUtterance = False

    if (prev_speaker == utterance[i].speaker):
        speakerChange = False
    else:
        speakerChange = True

    text_token=utterance[i].text
    features = [
        'speaker change=%s' % speakerChange,
        'first Utterance=%s' % firstUtterance,
        'text-token=%s' %text_token
    ]

    token_list = []
    pos_list = []

    if (utterance[i].pos != None):
        listofwords = utterance[i].pos

        for each_word in listofwords:
            new_token = "TOKEN_" + each_word.token
            new_pos = "POS_" + each_word.pos
            if each_word.token in string.punctuation:
                punct=True
            else:
                punct=False



            features.extend([
                'token.isPunctuation=%s' %punct

            ])


            token_list.append(new_token)
            pos_list.append(new_pos)

        for each_token in token_list:
            features.extend([
                'token=' + each_token

            ])

        token_last=token_list[-1]
        features.extend([
            'token_last=' + token_last

        ])

        for each_pos in pos_list:
            features.extend([
                'pos=' + each_pos

            ])


    return features


def extract_act_tag(utterance, i):
    act_tag = utterance[i].act_tag

    return act_tag


def sent2features(each_file):
    return [word2features(each_file, i) for i in range(len(each_file))]


def sent2labels(each_file):
    return [extract_act_tag(each_file, i) for i in range(len(each_file))]


def main():
    listOfCsvfiles = list(get_data(sys.argv[1]))

    for each_file in listOfCsvfiles:
        X_list = [sent2features(each_file)]
        Y_list = [sent2labels(each_file)]

        for xseq, yseq in zip(X_list, Y_list):
            trainer.append(xseq, yseq)

    # ---------Training the model starts---------- #
    trainer.set_params({
        'c1': 1.0,  # coefficient for L1 penalty
        'c2': 1e-3,  # coefficient for L2 penalty
        'max_iterations': 250,  # stop earlier
        'linesearch':"StrongBacktracking",

        # include transitions that are possible, but not observed
        'feature.possible_transitions': True
    })

    trainer.train('advanced_crf.crfsuite')
    # ---------Training the model ends---------- #


    # ----Tagging starts -----#
    tagger = pycrfsuite.Tagger()
    tagger.open('advanced_crf.crfsuite')



    #---extracting the dev data ------#
    listOfTestfiles = list(get_data(sys.argv[2]))

    dialog_filenames = sorted(glob.glob(os.path.join(sys.argv[2], "*.csv")))
    file_list = []
    for dialog_filename in dialog_filenames:
        head, tail = os.path.split(dialog_filename)
        file_list.append(tail)

    #---file number indexer -----#
    counter = 0

    output_file = sys.argv[3]
    try:
        os.remove(output_file)
    except OSError:
        pass
    f = open(output_file, "w", encoding="latin1")


    for each_file in listOfTestfiles:

        X_test = [sent2features(each_file)]

        Y_pred = [tagger.tag(xseq) for xseq in X_test]


        f.write("Filename= " + '"' + file_list[counter] + '"' + "\n")
        for each_filelabel in Y_pred:
            for each_label in each_filelabel:

                f.write(each_label)
                f.write("\n")

        counter = counter + 1

        f.write("\n")



if __name__ == "__main__":
    main()