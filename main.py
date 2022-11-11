import pandas as pd
import argparse  
import MeCab
import subprocess
import termextract.mecab
import termextract.core
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
tqdm.pandas()


cmd4='echo `mecab-config --dicdir`"/mecab-ipadic-neologd"'
path = (subprocess.Popen(cmd4, stdout=subprocess.PIPE,shell=True).communicate()[0]).decode('utf-8')                          
tagger=MeCab.Tagger("-d {0}".format(path))


parser = argparse.ArgumentParser(description='make keitaiso corpus')
parser.add_argument('file_path', help='curpus_file_path')
parser.add_argument('-k','--keitaiso',action='store_true')
parser.add_argument('-y','--yougo',action='store_true')
parser.add_argument('-s','--saisyou',action='store_true')

args = parser.parse_args()


corpus_file = pd.read_csv(args.file_path,sep='\t',header=None)

def term_word(mecab_1news,Threshold):
  word = [] #登場した名詞を重要度の高い順に格納する

  input_text = mecab_1news

  # 複合語を抽出し、重要度を算出
  frequency = termextract.mecab.cmp_noun_dict(input_text)
  LR = termextract.core.score_lr(frequency,
          ignore_words=termextract.mecab.IGNORE_WORDS,
          lr_mode=1, average_rate=1
      )
  term_imp = termextract.core.term_importance(frequency, LR)

  for key,value in term_imp.items():
    if float(value) >= float(Threshold):
      word.append(key)

  for i in range(len(word)):
    new = word[i].replace(' ', '')
    word[i] = new

  return word


def keitaiso(file):
  keyword_df = pd.DataFrame()

  df_train = file

  for row in df_train.itertuples():
    all_list = [[],[]]
    doc = str(row[1]).replace('option: ','')
    node = tagger.parseToNode(doc)
    term_mecab = tagger.parse(str(doc))
    first_node = node
    while node:
      node_list = node.feature.split(',')
      if node_list[0] != 'BOS/EOS':
        node_list.insert(0,node.surface)
        all_list[0].append(node_list)
      node=node.next
    doc_len = len(all_list[0])
    for i in range(len(all_list[0])):
      all_list[0][i].insert(0,i)
    c = 0
    del_list = []
    for i in range(len(all_list[0])):
      hitei = all_list[0][c][6]
      hinsi = all_list[0][c][2]
      genkei = all_list[0][c][8]
      if hinsi == '助動詞':
        if hitei == '特殊・ナイ' or hitei == '特殊・ヌ':
          sen = all_list[0][c-1][1] + all_list[0][c][1]
          del_list.append(c-1)
          del_list.append(c)
          j = 2
          while True:
            if all_list[0][c-j][2] != '動詞':
              break
            sen = all_list[0][c-j][1] + sen
            del_list.append(c-j)
            j  =j+1
          tokusyu = []
          tokusyu.append(all_list[0][c-1][0])
          tokusyu.append(sen)
          all_list[1].append(tokusyu)
      if hinsi == '形容詞':
        if hitei == '形容詞・アウオ段':
          if genkei == 'ない':
            sen = all_list[0][c-1][1] + all_list[0][c][1]
            tokusyu = []
            tokusyu.append(all_list[0][c-1][0])
            tokusyu.append(sen)
            all_list[1].append(tokusyu)
            del_list.append(c-1)
            del_list.append(c)
      c = c +1 
      for j in range(len(del_list)):
          del_num = del_list[j]
          for k in range(len(all_list[0])):
            if len(all_list[0][k]) != 0:
              if all_list[0][k][0] == del_num:
                all_list[0][k].clear()
    for i in range(len(all_list[0]),0,-1):
      if not all_list[0][i-1]:
        del all_list[0][i-1]
    for i in range(len(all_list[0]),0,-1):
      if not all_list[0][i-1]:
        del all_list[0][i-1]

    del_list = []
    for i in range(len(all_list[0])):
      dict_word = []
      if all_list[0][i][2] == '助詞':
        del_list.append(all_list[0][i][0])
      elif all_list[0][i][2] == '助動詞':
        del_list.append(all_list[0][i][0])
      elif all_list[0][i][2] == '形容詞' :
        dict_word.append(all_list[0][i][0])
        dict_word.append(all_list[0][i][8])
        all_list[1].append(dict_word)
        del_list.append(all_list[0][i][0])
      elif all_list[0][i][2] == '動詞':
        del_list.append(all_list[0][i][0])
        if all_list[0][i][1] == 'する' or all_list[0][i][1] == 'れる':
          pass
        else:
          dict_word.append(all_list[0][i][0])
          dict_word.append(all_list[0][i][8])
          all_list[1].append(dict_word)
      elif all_list[0][i][2] == '接続詞' or all_list[0][i][2] == '名詞':
        dict_word.append(all_list[0][i][0])
        dict_word.append(all_list[0][i][1])
        all_list[1].append(dict_word)
        del_list.append(all_list[0][i][0])
      elif all_list[0][i][2] == '記号':
        del_list.append(all_list[0][i][0])
        if all_list[0][i][1] == '、' or all_list[0][i][1] == '。':
          pass
        else:
          dict_word.append(all_list[0][i][0])
          dict_word.append(all_list[0][i][1])
          all_list[1].append(dict_word)
      elif all_list[0][i][2] == '副詞':
        del_list.append(all_list[0][i][0])
        if all_list[0][i][8] == 'どう' or all_list[0][i][8] == 'どうか':
          pass
        else:
          dict_word.append(all_list[0][i][0])
          dict_word.append(all_list[0][i][8])
          all_list[1].append(dict_word)
      elif all_list[0][i][2] == '連体詞':
        del_list.append(all_list[0][i][0])
        if all_list[0][i][8] == 'ある' or all_list[0][i][8] == 'その' or all_list[0][i][8] == 'どの':
          pass
        else:
          dict_word.append(all_list[0][i][0])
          dict_word.append(all_list[0][i][8])
          all_list[1].append(dict_word)
    for i in range(len(del_list)):
        del_num = del_list[i]
        for j in range(len(all_list[0])):
          if len(all_list[0][j]) != 0:
            if all_list[0][j][0] == del_num:
              all_list[0][j].clear()
    for i in range(len(all_list[0]),0,-1):
      if not all_list[0][i-1]:
        del all_list[0][i-1]
    if len(all_list[0]) != 0:
      for i in range(len(all_list[0])):
        if all_list[0][i][2] == '接頭詞':
          key_num = all_list[0][i][0]
          for j in range(len(all_list[1])):
            if all_list[1][j][0] == key_num:
              sen = all_list[1][j][1]
              sen = all_list[0][i][1] + sen
              all_list[1][j][1] = sen
    del all_list[0]
    new_all_list = []
    for i in range(doc_len):
      for j in range(len(all_list[0])):
        if all_list[0][j][0] == i:
          new_all_list.append(all_list[0][j])
    sen = ''
    for i in range(len(new_all_list)):
      sen = sen+ new_all_list[i][1]
      if i != len(new_all_list)-1:
        sen = sen + ' '
    new_row = pd.DataFrame([[sen,row[2]]])
    keyword_df = pd.concat([keyword_df,new_row])


  keyword_df= keyword_df.reset_index(drop=True)



def yougo(file):
  keyword_df = pd.DataFrame()
  df_train = file

  for row in df_train.itertuples():
    all_list = [[],[]]
    doc = str(row[1]).replace('option: ','')
    node = tagger.parseToNode(doc)
    term_mecab = tagger.parse(str(doc))
    first_node = node
    while node:
      node_list = node.feature.split(',')
      if node_list[0] != 'BOS/EOS':
        node_list.insert(0,node.surface)
        all_list[0].append(node_list)
      node=node.next
    doc_len = len(all_list[0])
    for i in range(len(all_list[0])):
      all_list[0][i].insert(0,i)
    c = 0
    del_list = []
    for i in range(len(all_list[0])):
      hitei = all_list[0][c][6]
      hinsi = all_list[0][c][2]
      genkei = all_list[0][c][8]
      if hinsi == '助動詞':
        if hitei == '特殊・ナイ' or hitei == '特殊・ヌ':
          sen = all_list[0][c-1][1] + all_list[0][c][1]
          del_list.append(c-1)
          del_list.append(c)
          j = 2
          while True:
            if all_list[0][c-j][2] != '動詞':
              break
            sen = all_list[0][c-j][1] + sen
            del_list.append(c-j)
            j  =j+1
          tokusyu = []
          tokusyu.append(all_list[0][c-1][0])
          tokusyu.append(sen)
          all_list[1].append(tokusyu)
      if hinsi == '形容詞':
        if hitei == '形容詞・アウオ段':
          if genkei == 'ない':
            sen = all_list[0][c-1][1] + all_list[0][c][1]
            tokusyu = []
            tokusyu.append(all_list[0][c-1][0])
            tokusyu.append(sen)
            all_list[1].append(tokusyu)
            del_list.append(c-1)
            del_list.append(c)
      c = c +1 
      for j in range(len(del_list)):
          del_num = del_list[j]
          for k in range(len(all_list[0])):
            if len(all_list[0][k]) != 0:
              if all_list[0][k][0] == del_num:
                all_list[0][k].clear()
    for i in range(len(all_list[0]),0,-1):
      if not all_list[0][i-1]:
        del all_list[0][i-1]
    word = term_word(term_mecab,0.7)
    if len(word) != 0:
      for i in range(len(word)):
        del_list = []
        existence = 0
        term = []
        for j in range(len(all_list[0])):
          if len(all_list[0][j]) != 0:
            if all_list[0][j][1] in word[i]:
              if existence == 0:
                term.append(all_list[0][j][0])
                term.append(word[i])
                all_list[1].append(term)
                del_list.append(all_list[0][j][0])
                existence = 1
              else:
                del_list.append(all_list[0][j][0])
        for j in range(len(del_list)):
          del_num = del_list[j]
          for k in range(len(all_list[0])):
            if len(all_list[0][k]) != 0:
              if all_list[0][k][0] == del_num:
                all_list[0][k].clear()
    for i in range(len(all_list[0]),0,-1):
      if not all_list[0][i-1]:
        del all_list[0][i-1]

    del_list = []
    for i in range(len(all_list[0])):
      dict_word = []
      if all_list[0][i][2] == '助詞':
        del_list.append(all_list[0][i][0])
      elif all_list[0][i][2] == '助動詞':
        del_list.append(all_list[0][i][0])
      elif all_list[0][i][2] == '形容詞' :
        dict_word.append(all_list[0][i][0])
        dict_word.append(all_list[0][i][8])
        all_list[1].append(dict_word)
        del_list.append(all_list[0][i][0])
      elif all_list[0][i][2] == '動詞':
        del_list.append(all_list[0][i][0])
        if all_list[0][i][1] == 'する' or all_list[0][i][1] == 'れる':
          pass
        else:
          dict_word.append(all_list[0][i][0])
          dict_word.append(all_list[0][i][8])
          all_list[1].append(dict_word)
      elif all_list[0][i][2] == '接続詞' or all_list[0][i][2] == '名詞':
        dict_word.append(all_list[0][i][0])
        dict_word.append(all_list[0][i][1])
        all_list[1].append(dict_word)
        del_list.append(all_list[0][i][0])
      elif all_list[0][i][2] == '記号':
        del_list.append(all_list[0][i][0])
        if all_list[0][i][1] == '、' or all_list[0][i][1] == '。':
          pass
        else:
          dict_word.append(all_list[0][i][0])
          dict_word.append(all_list[0][i][1])
          all_list[1].append(dict_word)
      elif all_list[0][i][2] == '副詞':
        del_list.append(all_list[0][i][0])
        if all_list[0][i][8] == 'どう' or all_list[0][i][8] == 'どうか':
          pass
        else:
          dict_word.append(all_list[0][i][0])
          dict_word.append(all_list[0][i][8])
          all_list[1].append(dict_word)
      elif all_list[0][i][2] == '連体詞':
        del_list.append(all_list[0][i][0])
        if all_list[0][i][8] == 'ある' or all_list[0][i][8] == 'その' or all_list[0][i][8] == 'どの':
          pass
        else:
          dict_word.append(all_list[0][i][0])
          dict_word.append(all_list[0][i][8])
          all_list[1].append(dict_word)
    for i in range(len(del_list)):
        del_num = del_list[i]
        for j in range(len(all_list[0])):
          if len(all_list[0][j]) != 0:
            if all_list[0][j][0] == del_num:
              all_list[0][j].clear()
    for i in range(len(all_list[0]),0,-1):
      if not all_list[0][i-1]:
        del all_list[0][i-1]
    if len(all_list[0]) != 0:
      for i in range(len(all_list[0])):
        if all_list[0][i][2] == '接頭詞':
          key_num = all_list[0][i][0]
          for j in range(len(all_list[1])):
            if all_list[1][j][0] == key_num:
              sen = all_list[1][j][1]
              sen = all_list[0][i][1] + sen
              all_list[1][j][1] = sen
    del all_list[0]
    new_all_list = []
    for i in range(doc_len):
      for j in range(len(all_list[0])):
        if all_list[0][j][0] == i:
          new_all_list.append(all_list[0][j])
    sen = ''
    for i in range(len(new_all_list)):
      sen = sen+ new_all_list[i][1]
      if i != len(new_all_list)-1:
        sen = sen + ' '
    new_row = pd.DataFrame([[sen,row[2]]])
    keyword_df = pd.concat([keyword_df,new_row])


  keyword_df= keyword_df.reset_index(drop=True)



def saisyou(file):
  keyword_df = pd.DataFrame()
  df_train = file

  for row in df_train.itertuples():
    all_list = [[],[]]
    doc = str(row[1]).replace('option: ','')
    node = tagger.parseToNode(doc)
    term_mecab = tagger.parse(str(doc))
    first_node = node
    while node:
      node_list = node.feature.split(',')
      if node_list[0] != 'BOS/EOS':
        node_list.insert(0,node.surface)
        all_list[0].append(node_list)
      node=node.next
    doc_len = len(all_list[0])
    for i in range(len(all_list[0])):
      all_list[0][i].insert(0,i)
    c = 0
    del_list = []
    for i in range(len(all_list[0])):
      hitei = all_list[0][c][6]
      hinsi = all_list[0][c][2]
      genkei = all_list[0][c][8]
      if hinsi == '助動詞':
        if hitei == '特殊・ナイ' or hitei == '特殊・ヌ':
          sen = all_list[0][c-1][1] + all_list[0][c][1]
          del_list.append(c-1)
          del_list.append(c)
          j = 2
          while True:
            if all_list[0][c-j][2] != '動詞':
              break
            sen = all_list[0][c-j][1] + sen
            del_list.append(c-j)
            j  =j+1
          tokusyu = []
          tokusyu.append(all_list[0][c-1][0])
          tokusyu.append(sen)
          all_list[1].append(tokusyu)
      if hinsi == '形容詞':
        if hitei == '形容詞・アウオ段':
          if genkei == 'ない':
            sen = all_list[0][c-1][1] + all_list[0][c][1]
            tokusyu = []
            tokusyu.append(all_list[0][c-1][0])
            tokusyu.append(sen)
            all_list[1].append(tokusyu)
            del_list.append(c-1)
            del_list.append(c)
      c = c +1 
      for j in range(len(del_list)):
          del_num = del_list[j]
          for k in range(len(all_list[0])):
            if len(all_list[0][k]) != 0:
              if all_list[0][k][0] == del_num:
                all_list[0][k].clear()
    for i in range(len(all_list[0]),0,-1):
      if not all_list[0][i-1]:
        del all_list[0][i-1]
    word = term_word(term_mecab,0.7)
    if len(word) != 0:
      for i in range(len(word)):
        del_list = []
        existence = 0
        term = []
        for j in range(len(all_list[0])):
          if len(all_list[0][j]) != 0:
            if all_list[0][j][1] in word[i]:
              if existence == 0:
                term.append(all_list[0][j][0])
                term.append(word[i])
                all_list[1].append(term)
                del_list.append(all_list[0][j][0])
                existence = 1
              else:
                del_list.append(all_list[0][j][0])
        for j in range(len(del_list)):
          del_num = del_list[j]
          for k in range(len(all_list[0])):
            if len(all_list[0][k]) != 0:
              if all_list[0][k][0] == del_num:
                all_list[0][k].clear()
    for i in range(len(all_list[0]),0,-1):
      if not all_list[0][i-1]:
        del all_list[0][i-1]

    del_list = []
    for i in range(len(all_list[0])):
      dict_word = []
      if all_list[0][i][2] == '助詞' or all_list[0][i][2] == '名詞' or all_list[0][i][2] == '助動詞':
        del_list.append(all_list[0][i][0])
      elif all_list[0][i][2] == '形容詞' :
        dict_word.append(all_list[0][i][0])
        dict_word.append(all_list[0][i][8])
        all_list[1].append(dict_word)
        del_list.append(all_list[0][i][0])
      elif all_list[0][i][2] == '動詞':
        del_list.append(all_list[0][i][0])
        if all_list[0][i][1] == 'する' or all_list[0][i][1] == 'れる':
          pass
        else:
          dict_word.append(all_list[0][i][0])
          dict_word.append(all_list[0][i][8])
          all_list[1].append(dict_word)
      elif all_list[0][i][2] == '接続詞':
        dict_word.append(all_list[0][i][0])
        dict_word.append(all_list[0][i][1])
        all_list[1].append(dict_word)
        del_list.append(all_list[0][i][0])
      elif all_list[0][i][2] == '記号':
        del_list.append(all_list[0][i][0])
        if all_list[0][i][1] == '、' or all_list[0][i][1] == '。':
          pass
        else:
          dict_word.append(all_list[0][i][0])
          dict_word.append(all_list[0][i][1])
          all_list[1].append(dict_word)
      elif all_list[0][i][2] == '副詞':
        del_list.append(all_list[0][i][0])
        if all_list[0][i][8] == 'どう' or all_list[0][i][8] == 'どうか':
          pass
        else:
          dict_word.append(all_list[0][i][0])
          dict_word.append(all_list[0][i][8])
          all_list[1].append(dict_word)
      elif all_list[0][i][2] == '連体詞':
        del_list.append(all_list[0][i][0])
        if all_list[0][i][8] == 'ある' or all_list[0][i][8] == 'その' or all_list[0][i][8] == 'どの':
          pass
        else:
          dict_word.append(all_list[0][i][0])
          dict_word.append(all_list[0][i][8])
          all_list[1].append(dict_word)
    for i in range(len(del_list)):
        del_num = del_list[i]
        for j in range(len(all_list[0])):
          if len(all_list[0][j]) != 0:
            if all_list[0][j][0] == del_num:
              all_list[0][j].clear()
    for i in range(len(all_list[0]),0,-1):
      if not all_list[0][i-1]:
        del all_list[0][i-1]
    if len(all_list[0]) != 0:
      for i in range(len(all_list[0])):
        if all_list[0][i][2] == '接頭詞':
          key_num = all_list[0][i][0]
          for j in range(len(all_list[1])):
            if all_list[1][j][0] == key_num:
              sen = all_list[1][j][1]
              sen = all_list[0][i][1] + sen
              all_list[1][j][1] = sen
    del all_list[0]
    new_all_list = []
    for i in range(doc_len):
      for j in range(len(all_list[0])):
        if all_list[0][j][0] == i:
          new_all_list.append(all_list[0][j])
    sen = ''
    for i in range(len(new_all_list)):
      sen = sen+ new_all_list[i][1]
      if i != len(new_all_list)-1:
        sen = sen + ' '
    new_row = pd.DataFrame([[sen,row[2]]])
    keyword_df = pd.concat([keyword_df,new_row])


  keyword_df= keyword_df.reset_index(drop=True)


if __name__ == '__main__':
  if args.keitaiso == True:
    keitaiso(corpus_file)
  if args.yougo == True:
    yougo(corpus_file)
  if args.saisyou == True:
    saisyou(corpus_file)
  