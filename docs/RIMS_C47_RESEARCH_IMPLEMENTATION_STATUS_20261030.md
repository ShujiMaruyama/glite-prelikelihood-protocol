# RIMS C47 — 実用的な受理状態監査・条件付き予言・独立対照

作成日：2026-10-30
著者：Shuji Maruyama (ORCID 0009-0007-5034-7634)
© 2026 Shuji Maruyama. All rights reserved.

## 実際に行ったこと

1. C46の「完全ビット一致」という説明と実装の差を発見・修正しました。C46はC `%a` 出力をPythonのfloatに変換した後 `==` を用いるため、正負ゼロを同一視します。C47では `struct.pack('>d', ...)` のバイト照合を追加し、前回COMMITより後、今回COMMITより前の成功済みDERIVだけに結合を限定しました。わざと符号付きゼロを反転した合成ログを使うと、旧C46ではマッチ1件、C47ではマッチ0件となることをテストで確認しました。
2. 凍結RIMS結合則の曲率差を、指数型結合の一次導関数一致を条件として厳密に導出：`Delta_kappa = -alpha_U^2/2 * sech^2[alpha_U*(phi-phi_t)]`。曲率そのものの最小位置 `s=2/3` とは異なり、比較差が最も大きいのは `s=1/2` である点を定量化しました。
3. 独立に測定可能だと仮定したbeta・kappaの誤差共分散を入力するCLIと、50,000件×4条件のガウス合成negative-control試験を作成しました。実測や本番観測尤度ではありません。
4. 既存61件＋新規44件＝105件のローカルPython/Cテストを実行し、すべてPASS。全105件を同梱して再現できます。

## 主な数値（条件付き仮定のみ）

- `alpha_U=0.01`, `s=0.65` では `beta=0.0035`, `kappa=-3.325e-5`, 一次結合を合わせた指数型との差は `-4.55e-5`。
- 仮定誤差 `(sigma_beta, sigma_kappa)=(5e-5,1e-5)` なら合成3sigma片側判定のpower = 93.804%、exponential-null false flag = 0.160%（50,000合成試行）。
- 曲率誤差を `4e-5` にすると `(sigma_beta=1e-4)` でpower = 3.118%。単に差があるだけでは現実の識別力はないことを定量的に示します。
- C44実CLASSで拒否された試行点の状態ベクトルは未COMMIT。C47新規実CLASS計算も行っていないため、**受理された物理状態のgは引き続き未測定**です。

## ファイル

- `paper/main.pdf`: 英文4ページの技術論文。先行研究の既知範囲・条件付き予言・実装欠陥修正・否定対照・残課題を記載。
- `src/c47_bitwise_join.py`: C43/C45a/C46ログからビット・ステップ区間で厳密照合。旧物理監査・原本検査を必ず通して、厳密判定を追加します。
- `src/c47_forecast.py`: 条件付き結合曲率式、共分散伝播、β不十分識別ゲート。
- `src/c47_montecarlo.py`: あらかじめ固定した4組の仮定誤差による合成negative-control検証。
- `tests/test_c47.py` と既存ソース：105件PASSの再現テスト。
- `results/`：JSON、CSV、テストログ。
- `figures/`：数式曲率・条件付き合成power（PNG・PDF）。
- `evidence/`：C46統合ZIP原本、C44実CLASS Run #2 Artifact原本。旧成果は変更しません。
- `PROVENANCE.json`、`SHA256SUMS.txt`：ハッシュと主張境界。

## 無課金の再現手順

LinuxのPython 3、NumPy、pytest、gccで、展開したフォルダから：

```bash
bash reproduce_static.sh
```

個別の仮定誤差設定：

```bash
python src/c47_forecast.py --output /tmp/c47_error_example.json \
  --alpha 0.01 --s 0.65 --relative-sigma-beta 0.01 \
  --relative-sigma-kappa 0.05 --corr 0.0
```

将来C43/C45a/C46の全トレースが得られたときだけ：

```bash
python src/c47_bitwise_join.py --stderr /path/to/native_stderr.txt \
  --output /path/to/new_strict_audit.json --alpha-U 0.01 \
  --phi-t -26.51196042031118
```

**注意：** `c47_bitwise_join.py`だけを実行しても実CLASS計算は起こらず、出力の数値が正常に見えても正式な物理安定性・ソース証明にはなりません。実測は元のpatch・CLASSバイナリ・入力ハッシュを同時監査した場合に限り解釈できます。

## 次のハードゲート

1. C45a/C46の計測器を固定CLASSに組み込み、元の物理条件・閾値を一切変更せず、ソース整合性とビルドを確立。
2. 計測ON/OFFで積分の受理履歴が変わらないかを厳密に比較（1回限定の原本試験の後、追加実行は別途許可）。
3. C47によりCOMMITと、同一完全状態で成功しているDERIVの物理量を厳密照合。ゼロ件なら「未観測」と判定。2点の直接実測値が受理軌道上で符号反転した場合に限り、同符号でない隣接COMMITのsign bracketを検討。
4. 背景成立、摂動の安全性、第二ソルバー、同条件の指数型／一般変化結合／ΛCDMとの真正比較を通過して初めて観測予言へ進む。

**現状で禁止する主張：** 新重力の発見、独自の観測的優越、検出、正規化背景解の成立、収束したMCMC、Bayes factor、受理状態の安定性証明。既存の変化結合と負のcoupling massに関する先行研究との差は厳格に区別します。