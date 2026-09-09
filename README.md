_This project has been created as part of the 42 curriculum by ktomita, tatsuzuki._

# A-maze-ing

## Description

TODO: 書く

---

## Instructions

TODO: 書く

```
make run
```

---

## Resources

### Websites

以下のWebサイトを参考にしました。

#### Pythonの仕様など

- [Python 3.14.7 Documentation](https://docs.python.org/3/index.html)
- [Pythonのメモリ管理: ガベージコレクション、弱参照、循環参照の問題と解決策 #Python - Qiita](https://qiita.com/Tadataka_Takahashi/items/a5d9654bba38d4eb3686)
- [【Python】抽象クラス・基底クラス・抽象基底クラスの違いをわかりやすく解説！ - IT Information](https://it-infomation.com/python-base-class-abstract-class-abstract-base-class/)
- [printで色をつける方法 | Python学習講座](https://www.python.ambitious-engineer.com/archives/3721)

#### 迷路生成アルゴリズム

- [13 Maze Generation Algorithms Visualized (with Sound) | 迷路生成アルゴリズム全13種を見比べる - YouTube](https://www.youtube.com/watch?v=Y6Ijgl0iZb0)
- [自動生成迷路](https://www5d.biglobe.ne.jp/stssk/maze/make.html)
- [ランダムに迷路生成したい［棒倒し法］｜つけらっとゲームス](https://note.com/tsukerat_games/n/nfd7ae53371ae)
- [【よくわかる】迷路生成アルゴリズム「棒倒し法」を説明！](https://minatame-lab.com/maze-stick/)
- [迷路作成アルゴリズムまとめ](https://zenn.dev/megeton/articles/5b16208f5d9678)
- [C言語：棒倒し法でダンジョン(迷路)を表現する | 電脳産物](https://dianxnao.com/c%E8%A8%80%E8%AA%9E%EF%BC%9A%E6%A3%92%E5%80%92%E3%81%97%E6%B3%95%E3%81%A7%E3%83%80%E3%83%B3%E3%82%B8%E3%83%A7%E3%83%B3%E8%BF%B7%E8%B7%AF%E3%82%92%E8%A1%A8%E7%8F%BE%E3%81%99%E3%82%8B/)
- [穴掘り法を使って迷路を作ろう #Python - Qiita](https://qiita.com/naru_1017/items/e4d017433372a313aeb3)
- [迷路生成(穴掘り法) - Algoful](https://algoful.com/Archive/Algorithm/MazeDig)
- [ターミナルプロンプトの表示・色の変更 #Linux - Qiita](https://qiita.com/hmmrjn/items/60d2a64c9e5bf7c0fe60)
- [倒すって英語でなんて言うの？ - DMM英会話なんてuKnow?](https://eikaiwa.dmm.com/uknow/questions/59114/)
- [穴掘り法を使って迷路を作ろう #Python - Qiita](https://qiita.com/naru_1017/items/e4d017433372a313aeb3)
- [sazameki/maze-algorithms: 迷路生成の各種アルゴリズムのC++実装 (Win/Mac両対応)](https://github.com/sazameki/maze-algorithms)

### AI Usage

私たちはAIを以下の用途に利用しました。

- 検索
- トラブルシューティング
- Pull Requestやコミットメッセージの文章の生成
- [...]

私たちはGitHubのPull Requestの機能や、お互いのレビューやコミュニケーションを通じて常にコードについて議論しました。特に、今回の課題で重要となる迷路のアルゴリズムについてはすべて手動で書き、お互いに理解を深めるために時間をかけて話し合いました。

---

## Additions according to the subject

これらのこと以外に課題で追加で求められていることについて、以下に記します。

### Structure of the repository

### Algorithm Choice

棒倒しで実装したが42入れたらうまく行かなくて穴掘り法にした

#### Why?

利用可能なマスに制限があったため

### Reuseability

クラスをインポートする

### Team Management

2人で開発をしました。以下に、それぞれが中心的に担当したことと、2人で協力して行ったことを記します。

#### ktomita

- 穴掘り法と、提出しなかった棒倒し法の迷路生成のアルゴリズムの作成
- 42を含めた / 含めない迷路の生成

#### tatsuzuki

- Configのパースとエラーハンドリング、テスト
- 生成された迷路のファイルへの出力
- ターミナルへの出力の整形
- Makefileやpyproject.tomlなどの環境構築

#### 2人でやったこと

- データ構造や全体の設計の決定や計画
- 相互のコードのレビュー
- 例外ケースやエラーの発見

#### Planning

#### Things worked / Things can be improved

#### Used tools

パッケージマネージャおよびPythonの実行環境の管理に `uv` を利用しました。
