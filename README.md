# corpus_Keywording


## termextractの準備
*ABCIで使用する場合のみ実行*
termextractをビルドするためのフォルダが必要となる。
自分のホームディレクトリ、もしくは専用のフォルダを準備する。


*インストール手順*
以下のコードを実行する
1. `wget http://gensen.dl.itc.u-tokyo.ac.jp/soft/pytermextract-0_02.zip`
2. `unzip /content/pytermextract-0_02.zip`
3. `python setup.py install`

*ABCIの場合*

3. `python setup.py install --home=<dir>`
`<dir>`の部分に自分の指定するフォルダのPath入れる


## ライブラリのimport 
以下のコードを実行する
`pip install -r requirements.txt`

