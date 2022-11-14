import pandas as pd
import argparse  
import MeCab
import subprocess


cmd4='echo `mecab-config --dicdir`"/mecab-ipadic-neologd"'
path = (subprocess.Popen(cmd4, stdout=subprocess.PIPE,shell=True).communicate()[0]).decode('utf-8')                          
tagger=MeCab.Tagger("-d {0}".format(path))


parser = argparse.ArgumentParser(description='make keitaiso corpus')
parser.add_argument('file_path', help='curpus_file_path')

args = parser.parse_args()


corpus_file = pd.read_json(args.file_path,orient='records', lines=True)

def keitaiso(file):
  keyword_df = pd.DataFrame(columns=['in','out'])

  df_train = file

  for row in df_train.itertuples():
    all_list = [[],[]]
    doc = str(row[1]).replace('option: ','')
    node = tagger.parseToNode(doc)
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
    new_row = pd.DataFrame([[sen,row[2]]],columns=['in','out'])
    keyword_df = pd.concat([keyword_df,new_row])


  keyword_df= keyword_df.reset_index(drop=True)
  new_path = args.file_path.replace('.jsonl','')
  keyword_df.to_json(new_path+'_keitaiso.jsonl', orient='records', force_ascii=False, lines=True)







if __name__ == '__main__':
    keitaiso(corpus_file)

  