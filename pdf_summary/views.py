from django.shortcuts import render, redirect, get_object_or_404
import os
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import requests
import io
import fitz  # PyMuPD
from langchain.schema import Document
from urllib.parse import urlparse
from django.conf import settings
from .models import PDFSummary, ChatLog
import shutil

# 環境変数読み込み
openai_api_key = settings.OPENAI_API_KEY
langchain_api_key = settings.LANGCHAIN_API_KEY
openai_api_base = settings.OPENAI_API_BASE

# Create your views here.
##############RAGで使う関数#########################
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["OPENAI_API_KEY"] = openai_api_key 
os.environ["LANGCHAIN_API_KEY"] = langchain_api_key
llm = ChatOpenAI(model="gpt-4o-mini", openai_api_base=openai_api_base)

embeddings = OpenAIEmbeddings(openai_api_base=openai_api_base)


def get_pdf_url(pdf_url):
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()  # ステータスコードを確認
        pdf_file = io.BytesIO(response.content)
        pdf_document = fitz.open(stream=pdf_file, filetype="pdf")

        result = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            result += page.get_text()
        pdf_document.close()

        return result
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None

def get_pdf_file(pdf_file):
    try:
        # PDFをメモリ上で開く
        document = fitz.open("pdf", pdf_file.read())
        text = "".join(page.get_text() for page in document)
        document.close()

        return text

    except Exception as e:
        print(f"PDF処理中にエラーが発生しました: {e}")
        return None


    except Exception as e:
        print(f"PDF処理中にエラーが発生しました: {e}")
        return None

def create_vectorstore(url,file, vectorstore_name):
    try:
        print("ベクトルストア作成中")
        vectorstore_dir = os.path.join(settings.VECTORSTORE_DIR, vectorstore_name)
        if not os.path.exists(vectorstore_dir):
            os.makedirs(vectorstore_dir)
        print(vectorstore_dir)

        # PDFからテキストを取得
        if url == None:
            result = get_pdf_file(file)
        elif file == None:
            result = get_pdf_url(url)
        else:
            result_file=get_pdf_file(file)
            result_url=get_pdf_url(url)
            result = result_file+result_url
        if not result:
            raise ValueError("PDFからテキストを取得できませんでした。")

        docs = [Document(page_content=result, metadata={})]

        # テキスト分割
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)

        # ベクトルストアの作成
        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory=vectorstore_dir)
        return vectorstore,vectorstore_dir

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None


def format_docs(docs_list):
    return "\n\n".join(doc.page_content for doc in docs_list)

def create_rag_chain(vectorstore):
    retriever = vectorstore.as_retriever()
    prompt = hub.pull("rlm/rag-prompt")
    return (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
###################################################


def index(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        pdf_url = request.POST.get('url')
        pdf_file = request.FILES.get('pdf_file')
        pdf_file_name = None  
        if not pdf_url and not pdf_file:
            return render(request, 'pdf_summary/index.html', {
                'pdf_list': PDFSummary.objects.all(),
                'error_message': 'urlかファイル、少なくとも1つは入力してください'
            })
        try:
            if pdf_url and not pdf_file:
                # ベクトルストア作成
                vectorstore,vectorstore_dir = create_vectorstore(pdf_url,None, name)
                # RAGチェーン作成
                rag_chain = create_rag_chain(vectorstore)
            elif not pdf_url and pdf_file:
                    pdf_file_name = pdf_file.name
                    vectorstore,vectorstore_dir = create_vectorstore(None,pdf_file, name)
                    rag_chain = create_rag_chain(vectorstore)
            else:
                vectorstore,vectorstore_dir = create_vectorstore(pdf_url,pdf_file, name)
                rag_chain = create_rag_chain(vectorstore)
                pdf_file_name = pdf_file.name
                

            # PDFの要約を生成
            summary = rag_chain.invoke('このPDFを分かりやすく丁寧に要約してください！')

            # モデル保存
            PDFSummary.objects.create(
                name=name,
                pdf_url=pdf_url,
                pdf_file_name=pdf_file_name,
                vectorstore_path=vectorstore_dir,
                summary=summary
            )

            return redirect('index')
        
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            # 必要に応じてエラーメッセージをテンプレートに渡す
            return render(request, 'pdf_summary/index.html', {
                'pdf_list': PDFSummary.objects.all(),
                'error_message': 'PDFの要約中にエラーが発生しました。もう一度試してください。'
            })
    pdf_list = PDFSummary.objects.all()
    return render(request,'pdf_summary/index.html',{'pdf_list':pdf_list})

def detail(request,pk):
    pdf_summary = get_object_or_404(PDFSummary, pk=pk)
    chat_logs = pdf_summary.chat_logs.all()
    vectorstore_path = pdf_summary.vectorstore_path

    if request.method == 'POST':
        question = request.POST.get('question')
        vectorstore = Chroma(persist_directory=vectorstore_path, embedding_function=embeddings)
        rag_chain = create_rag_chain(vectorstore)
        answer = rag_chain.invoke(question)

        ChatLog.objects.create(
            pdf_summary=pdf_summary,
            question=question,
            answer=answer
        )

        return redirect('detail',pk=pdf_summary.pk)


    return render(request,'pdf_summary/detail.html',
                  {'pdf_summary': pdf_summary,'chat_logs':chat_logs})



def delete_pdf(request,pk):
    pdf_summary = get_object_or_404(PDFSummary,pk=pk)
    if pdf_summary.vectorstore_path:
        print(f"ベクトルストアの名前：{pdf_summary.vectorstore_path}")
        path = pdf_summary.vectorstore_path
        pdf_summary.delete()
        try:
            shutil.rmtree(path)
        except Exception as e:
            print(f"フォルダ削除失敗: {e}")
    return redirect('index')

