# コマンド集 ver 0.1
# 2024/2/20

# git commandが使えることを確認
git --version
# sam commandが使えることを確認
sam --version

# commitの作成者名・メールアドレス設定（例：--global(optional)
git config --global user.name "endl"
git config --global user.email endl12028@gmail.com

# template.yaml有効性検証
sam validate

# デプロイ実行
sam deploy
