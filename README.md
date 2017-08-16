ClickScraper
====

Overview
クリック証券のマイページからいくつかの値を抽出します。

## Description

## Requirement
Python 2.7
BeautifulSoup4
Selenium
PhantomJS

## Usage

###・全てをzipで固めてLambdaにアップロードして利用します。
    `zip -r upload.zip *`

###・Lambdaの環境変数にUSERNAMEとPASSWORDを指定してください。

###・self.BUCKET_NAMEに出力したいS3バケットの名前を指定してください。

###・権限まわり
  Lambdaの実行権限(暗黙的にCloudWatchの書き込み権限を含む)に加え、S3への書き込み権限をIAMにて付与してください。

###・実行結果はS3に、ログはCloudWatchに吐かれます。

###・S3に吐かれるファイルの見方
`json/out.json`
      出力したJSONファイル
`logs/***.html`
      解析するHTMLファイル javascriptも実行され、改変後の状態になっているため、
      結果が意図しないものになっている場合はこれの該当箇所を参照すると良いかと思われる
`screenshots/***.png`
      解析するHTMLファイルをレンダリングしたもの。
      Lambdaが日本語フォントを持っておらず日本語部分は正しく表示できないため、参考程度に。

## Install

## Contribution

## Licence

## Author

kentoku24
