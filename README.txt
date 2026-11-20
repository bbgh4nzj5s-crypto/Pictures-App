PCなし・GitHub Actionsで画像ZIPを作る補助ファイル

【内容】
- download_images.py：公式サイトのおねがい1〜4だんのサムネイル画像を取得してZIP化
- .github/workflows/make-image-zip.yml：GitHub Actionsから実行する設定

【手順】
1. 既存の本番アプリとは別に、GitHubで新しいプライベートリポジトリを作る。
2. この2つのファイルを、ZIP内のフォルダ構成どおりにリポジトリにアップロードする。
3. GitHubのActions → Make image ZIP (personal use) → Run workflow を選択。
4. 完了後、実行ページのArtifacts内「coordinate-image-zip」をダウンロード。
5. iPhoneの「ファイル」アプリでZIPを展開する。中の aipri_images_....zip も展開する。
6. 利用中のWebアプリの設定 →「画像を選ぶ(複数可)」で展開後の画像をまとめて選ぶ。

【注意】
- GitHub Actions上で実行して初めて画像入りZIPができます。配布ZIP自体に公式画像は含みません。
- 公式サイトの構造変更、通信制限、画像ファイル名の違いで、一部取得・割当できない場合があります。
- 実際のアプリ側がファイル名を認識するかは未検証です。
- 画像をGitHub等で公開・再配布しないでください。権利者の利用条件を守り、個人利用の範囲にとどめてください。
- 本番アプリのリポジトリには追加しないでください。
