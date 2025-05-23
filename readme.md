# 这是一个基于Migic_pdf的webapi实现demo，可以直接使用docker部署

# docker build （要装依赖和model，build要挺久的）
docker build -t magic-pdf-webapi .

# docker run
docker run -d -p 8000:8000 --name pdf-webapi magic-pdf-webapi

# 运行后就可以使用postman调接口了
curl --location 'http://127.0.0.1:8000/pdf2mdUpload' \
--form 'file=@"/D:/Test/需要转换的pdf.pdf"'
