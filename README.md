## `mazegen` モジュールの使い方

`src/mazegen` は他プロジェクトからそのまま import して使える、迷路生成ロジックの単独モジュールです。

### 基本的な使い方

`MazeGenerator` は `Config` インスタンスを受け取って初期化します。

```python
from mazegen import MazeGenerator, Config

config = Config.model_validate({
    "width": "15",
    "height": "15",
    "entry": "0,0",
    "exit": "14,14",
    "output_file": "maze.txt",
})

maze_gen = MazeGenerator(config)
maze_gen.generate_data()   # 迷路と最短経路を生成
maze_gen.print_board()     # ターミナルに盤面を出力
```

### カスタムパラメータの指定

`Config` の各フィールドは以下の通りです（`model_validate` に渡す辞書の値は全て文字列）。

| キー          | 説明                                           | 例                   |
| ------------- | ---------------------------------------------- | -------------------- |
| `width`       | 迷路の幅（セル数、3〜100）                     | `"15"`               |
| `height`      | 迷路の高さ（セル数、3〜100）                   | `"15"`               |
| `entry`       | 入口セルの座標 `"x,y"`                         | `"0,0"`              |
| `exit`        | 出口セルの座標 `"x,y"`                         | `"14,14"`            |
| `output_file` | 生成結果を書き出すファイルパス                 | `"maze.txt"`         |
| `perfect`     | ループなしの完全迷路にするか（省略時 `False`） | `"True"` / `"False"` |
| `seed`        | 乱数シード（省略時はランダム）                 | `"42"`               |

```python
config = Config.model_validate({
    "width": "21",
    "height": "21",
    "entry": "0,0",
    "exit": "20,20",
    "output_file": "maze.txt",
    "perfect": "True",
    "seed": "42",
})
maze_gen = MazeGenerator(config)
```

CLIから設定ファイル（`KEY=VALUE` 形式）を読み込んで `Config` を作りたい場合は `arg_parse()` を使います（`sys.argv` からファイルパスを受け取ります）。

```python
from mazegen import arg_parse, MazeGenerator

config = arg_parse()
maze_gen = MazeGenerator(config)
```

### 生成結果へのアクセス

`generate_data()` 実行後、以下の属性から生成結果を参照できます。

- `maze_gen.board`: `list[list[FillStatus]]`。盤面全体。各セルは `mazegen.types.FillStatus`（`empty` / `wall` / `entry` / `exit` など）。
- `maze_gen.path`: `set[tuple[int, int]] | None`。入口から出口までの最短経路上の座標集合（`board` 上の座標系、入口・出口自体は含まない）。
- `maze_gen.path_direction`: `str`。最短経路を入口から出口まで辿った移動方向を `N`/`S`/`E`/`W` で連結した文字列。
- `maze_gen.config.entry` / `maze_gen.config.exit`: 入口・出口のセル座標（`board` 座標系では `x*2+1, y*2+1`）。

```python
maze_gen.generate_data()

print(maze_gen.path_direction)   # 例: "SSEENNSS..."
print(len(maze_gen.path))        # 経路長

# 盤面をテキストとして出力ファイルに書き出す（entry/exit座標・経路方向も含む）
maze_gen.generate_output()
```
