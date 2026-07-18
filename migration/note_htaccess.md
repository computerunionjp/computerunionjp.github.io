# .htaccess の設定変更

## 静的ページとPHPの優先順位

```apache
DirectoryIndex index.php index.html
```

変更

```apache
DirectoryIndex index.html index.php
```

## 国別アクセス制御

```apache
SetEnvIf Request_URI ".*" AllowCountry
```

削除

## REST API

```apache
SetEnvIf Request_URI ".*" AllowRestApi
```

削除

```apache
# For WordPress REST API Basic authentication
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteCond %{HTTP:Authorization} .
RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]
</IfModule>
```

削除

## HTTPS 強制

```apache
# Force https
RewriteEngine On
RewriteCond %{HTTPS} !=on
RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [R=301]
```

変更無し

## CCUブログ目次

```apache
# Redirect CCU Blog
RewriteCond %{QUERY_STRING} page_id=1447$
RewriteRule ^ https://ccu.or.jp/category/blog/? [R=302]
```

変更無し

## 「労働者供給事業」ページ

```apache
RewriteCond %{QUERY_STRING} page_id=(2|2975|37|387|39|43|45|47|49)$
RewriteRule ^ https://%{HTTP_HOST}?page_id=4732 [R=302]
```

変更

```apache
RewriteCond %{QUERY_STRING} page_id=(2|2975|37|387|39|43|45|47|49|4732)$
RewriteRule ^$ /rokyo/? [R=302,L]
```

## 「労供事業の契約の形」ページ

追加

```apache
RewriteCond %{QUERY_STRING} (^|&)page_id=4539(&|$)
RewriteRule ^$ /rokyo/details/? [R=302,L]
```

## 「プライバシーポリシー」ページ

追加

```apache
RewriteCond %{QUERY_STRING} (^|&)page_id=6821(&|$)
RewriteRule ^$ /policy/? [R=302,L]
```

## 「お問い合わせ」ページ

RewriteCond %{QUERY_STRING} page_id=(200|29|53)$
RewriteRule ^ https://%{HTTP_HOST}?page_id=4650 [R=302]

変更

```apache
RewriteCond %{QUERY_STRING} page_id=(200|29|53|4650)$
RewriteRule ^$ /contact/? [R=302,L]
```

## 「労供事業の組合員の声」ページ

```apache
RewriteCond %{QUERY_STRING} page_id=438$
RewriteRule ^ https://%{HTTP_HOST}?page_id=4549 [R=302]
```

変更

```apache
RewriteCond %{QUERY_STRING} (^|&)page_id=(438|4549)(&|$)
RewriteRule ^$ /rokyo/testimonials/? [R=302,L]
```

## 「ブログ」目次

```apache
RewriteCond %{QUERY_STRING} page_id=3635$
RewriteRule ^ https://%{HTTP_HOST}?cat=10 [R=302]
```

変更

```apache
RewriteCond %{QUERY_STRING} (^|&)page_id=3635(&|$)
RewriteCond %{QUERY_STRING} (^|&)cat=10(&|$)
RewriteRule ^$ /blog/? [R=302,L]
```

## 「ブログ」記事

追加

```apache
RewriteCond %{QUERY_STRING} (^|&)p=()3583|3588|3593|3600|3607|3611|3615|3618|3620|4473|4475|4482|4488|4493|4498|4776|4779|4784|4786|4790|4794|4798|4800|5227|5231|5233|5239|5243|5246|5590|5593|5599|5601|5606|5609|5611|5614|5616|5724|5726|5769|5771|5774|5776|5778|5780|5789|5791|5795|5798|5844|5846|5848|6093|6095|6104|6111|6118|6121|6124|6126|6129|6134|6173|6222|6224|6226|6371|6394|6426|6433|6437|6439|6441|6443|6445|6488|6567|6569|6571|6622|6640|6644|6707|6713|6722|6799|6803|6805|6934|6940|7001|7008|7010|7044|7053|7056|7110|7116|7119|7194|7199|7201|7251|7405|7415|7433|7461|7487|7523|7594|7596|7738|7742|7744|7746|7751|7753|7758|7763|7765|7769|7771|7774|7776|7793|7801|7803|7831|7833|7860|7872|7885|7887|7889|7912|7932|7934|7953|7974|7985|7999|8016|8028(&|$)
RewriteRule ^$ /blog/%2/? [R=302,L]
```

## 「しごと情報」目次

追加

```apache
RewriteCond %{QUERY_STRING} (^|&)cat=5(&|$)
RewriteRule ^$ /job/? [R=302,L]
```

## 「しごと情報」記事

「ブログ」記事の設定より後に追加

```apache
RewriteCond %{QUERY_STRING} (^|&)p=([0-9]+)(&|$)
RewriteRule ^$ /job/%2/? [R=302,L]
```

## その他の古いページ

```apache
RewriteCond %{QUERY_STRING} page_id=(2208|33|35|41)$
RewriteRule ^ https://%{HTTP_HOST}? [R=302]
```

変更

```apache
RewriteCond %{QUERY_STRING} page_id=(2208|33|35|41)$
RewriteRule ^$ /? [R=302,L]
```

## 「お探しのページが見つかりません」

追加

```apache
ErrorDocument 404 /404.html
```
