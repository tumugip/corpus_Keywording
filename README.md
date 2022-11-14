# corpus_Keywording

`main_jsonl.py`:３種類のキーワード化をすることができます
`light_main_jsonl`:termextractを使用しないキーワード化ができます


## termextractの準備
*ABCIで使用する場合のみ実行*  
termextractをビルドするためのフォルダが必要となる。  
自分のホームディレクトリ、もしくは専用のフォルダを準備する。


*インストール手順*
以下のコードを実行する
1. `wget http://gensen.dl.itc.u-tokyo.ac.jp/soft/pytermextract-0_02.zip`
2. `unzip 先ほどダウンロードしたファイルのパス`
3. `python setup.py install`

*ABCIの場合*

3. `python setup.py install --home=<dir>`
`<dir>`の部分に自分の指定するフォルダのPath入れる



## mecabの準備

*~~ABCIにmecabを導入する~~*

~~ABCIはCentOSなので、yumを使用してMecabを入れるらしい~~

上手く入れられないので断念
皆様ローカルでやってください・・・


*ローカルにmecabを導入する*  
brewでインストール  
`brew install mecab`  
mecabで利用するメジャーな辞書であるIPA辞書も一緒にインストールしておく　　  
`brew install mecab-ipadic`

*ローカルにneologdを導入する*  
皆様、新しい固有表現が入った辞書どこかにないかな？と思ったことありませんか？  
ということで、追加で辞書を入れる  

下準備
`brew install curl xz`

公式のページには
`C++コンパイラ iconv(libconv) mecab mecab-ipadic xz`と書いてありますが、調べてみた感じ、上記の二つだけでどうにかなりそうな感じがします。
足りないものがあったら、随時インストールしてください。

以下公式のGithubのページになりますので、こちらを参考にしてください  
[neologd/README.ja](https://github.com/neologd/mecab-ipadic-neologd/blob/master/README.ja.md)


インストール
`git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git`

`cd mecab-ipadic-neologd`

`./bin/install-mecab-ipadic-neologd -n`
確認画面で`yes`を入力すると、sudo 権限で最新版がインストール(初回実行時以降は更新)されます。


インストール先はオプション未指定の場合 mecab-config によって決まります。
一旦確認してみましょう。

``echo `mecab-config --dicdir`"/mecab-ipadic-neologd"``

標準インストールだと、一部の辞書はインストールされません。全部の辞書を使いたい時は以下のコマンドを使用してください。

`./bin/install-mecab-ipadic-neologd -n -a`


## ライブラリのimport 
以下のコードを実行する  
`pip install -r requirements.txt`

