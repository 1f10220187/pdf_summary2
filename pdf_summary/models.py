from django.db import models

# Create your models here.
from django.db import models

class PDFSummary(models.Model):
    # PDFの名前（ユーザーが設定する名前）
    name = models.CharField(max_length=255)
    
    # PDFのURL
    pdf_url = models.URLField(null=True, blank=True)

    # アップロードしたPDFファイル
    pdf_file_name = models.TextField(null=True, blank=True)
    
    # ベクトルストアの保存パス
    vectorstore_path = models.TextField()
    
    # 要約結果
    summary = models.TextField(null=True, blank=True)
    
    # 作成日時
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class ChatLog(models.Model):
    pdf_summary = models.ForeignKey('PDFSummary', on_delete=models.CASCADE, related_name='chat_logs')
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat with {self.pdf_summary.name} at {self.created_at}"
